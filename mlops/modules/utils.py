from typing import List, Optional

import keras_tuner as kt
import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow_decision_forests as tfdf
import tensorflow_transform as tft
import tfx.v1 as tfx
from tensorflow_addons.utils.types import AcceptableDTypes
from tfx_bsl.public import tfxio


class F1ScoreBinaryBridge(tfa.metrics.F1Score):
    def __init__(
        self,
        num_classes: int = 2,
        average: Optional[str] = None,
        threshold: float = 0.5,
        name: str = "f1_score",
        dtype: AcceptableDTypes = None,
    ):
        super().__init__(num_classes, average, threshold, name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true_ohe = tf.one_hot(tf.cast(tf.squeeze(y_true), tf.int32), depth=2)
        y_pred_ohe = tf.one_hot(
            tf.cast(tf.math.greater(tf.squeeze(y_pred), self.threshold), tf.int32),
            depth=2,
        )
        return super().update_state(y_true_ohe, y_pred_ohe, sample_weight)


# Unfortunately, not suitable yet for our models [GBTM, RFM, CM]
# Only support for Distributed Gradient Boosted Trees models [DGBTM]
# See: https://www.tensorflow.org/decision_forests/distributed_training
# def get_training_strategy():
#     list_gpu = tf.config.list_physical_devices("GPU")
#     if len(list_gpu) == 1:
#         strategy = tf.distribute.OneDeviceStrategy("/gpu:0")
#     elif len(list_gpu) > 1:
#         strategy = tf.distribute.MirroredStrategy()
#     else:
#         strategy = tf.distribute.OneDeviceStrategy("/cpu:0")
#     return strategy


def _model_compiler(
    model: tf.keras.Model,
    threshold: Optional[float] = 0.5,
) -> tf.keras.Model:
    model.compile(
        metrics=[
            tf.keras.metrics.BinaryAccuracy(threshold=threshold),
            tf.keras.metrics.AUC(curve="ROC"),
            # In this case to evaluate F1-Score properly we need to do One-Hot first
            F1ScoreBinaryBridge(average="macro", threshold=threshold),
        ]
    )
    return model


def gbtm_builder(
    hparams: kt.HyperParameters,
    preprocessing: Optional[tf.keras.Model] = None,
) -> tf.keras.Model:
    model = tfdf.keras.GradientBoostedTreesModel(
        preprocessing=preprocessing,
        num_trees=hparams.get("num_trees"),
        max_depth=hparams.get("max_depth"),
        min_examples=hparams.get("min_examples"),
        task=tfdf.keras.Task.CLASSIFICATION,
        verbose=0,
    )
    return _model_compiler(model, hparams.get("threshold"))


def rfm_builder(
    hparams: kt.HyperParameters,
    preprocessing: Optional[tf.keras.Model] = None,
) -> tf.keras.Model:
    model = tfdf.keras.RandomForestModel(
        preprocessing=preprocessing,
        num_trees=hparams.get("num_trees"),
        max_depth=hparams.get("max_depth"),
        min_examples=hparams.get("min_examples"),
        task=tfdf.keras.Task.CLASSIFICATION,
        verbose=0,
    )
    return _model_compiler(model, hparams.get("threshold"))


def cm_builder(
    hparams: kt.HyperParameters,
    preprocessing: Optional[tf.keras.Model] = None,
) -> tf.keras.Model:
    model = tfdf.keras.CartModel(
        preprocessing=preprocessing,
        max_depth=hparams.get("max_depth"),
        min_examples=hparams.get("min_examples"),
        task=tfdf.keras.Task.CLASSIFICATION,
        verbose=0,
    )
    return _model_compiler(model, hparams.get("threshold"))


def transformed_name(key: str) -> str:
    """Renaming transformed features"""
    return key + "_xf"


def _gzip_reader_fn(filenames: tf.string) -> tf.data.Dataset:
    """Loads compressed data (e.g. data_tfrecord-xxx.gzip)

    Args:
        filenames: A tf.string tensor or tf.data.Dataset containing
            one or more filenames with gzip extension.
    Returns:
        TFRecordDataset object
    """
    return tf.data.TFRecordDataset(filenames=filenames, compression_type="GZIP")


# This method is alternative method to reduce dimension inputs with squeeze feature spec
# @tf.autograph.experimental.do_not_convert
# def sqz_feature_spec_from_tfm_output(tf_transform_output, raw_output=False):
#     """This function is for squeeze (reduce) the dimention of the input data
#     to match Decision Forest model input requirements.

#     Args:
#         tf_transform_output: data schema to load the dataset from TFRecord
#             data structures generated by Transform component
#     Returns:
#         squeezed feature spec that will help to reduce dimention of
#         the input data
#     """

#     squeezed_feature_spec = {}
#     if raw_output:
#         feature_spec = tf_transform_output.raw_feature_spec().copy()
#     else:
#         feature_spec = tf_transform_output.transformed_feature_spec().copy()
#     for feature_name in feature_spec:
#         # In this case, the dataset only consist FixedLenFeature without VarLenFeature
#         if type(feature_spec[feature_name]) == tf.io.FixedLenFeature:
#             squeezed_feature_spec[feature_name] = tf.io.FixedLenFeature(
#                 shape=[],
#                 dtype=feature_spec[feature_name].dtype,
#                 default_value=feature_spec[feature_name].default_value,
#             )
#     return squeezed_feature_spec


def input_fn_v3(
    file_pattern: List[str],
    tf_transform_output: tft.TFTransformOutput,
    batch_size: int,
    label_key: str,
) -> tf.data.Dataset:
    """Generates a dataset (features and label) for training and tuning process.

    Args:
        file_pattern: list of paths or patterns of input tfrecord files
        tf_transform_output: data schema to load the dataset from TFRecord
            data structures generated by Transform component
        batch_size: representing the number of consecutive elements of returned
            dataset to combine in a single batch
        label_key: feature key of dataset for label (target feature)

    Returns:
        A dataset that contains (features, indices) tuple where features is a
            dictionary of Tensors, and indices is a single Tensor of label indices.
    """

    # transformed_feature_spec = sqz_feature_spec_from_tfm_output(tf_transform_output)
    transformed_feature_spec = tf_transform_output.transformed_feature_spec().copy()
    transformed_label = transformed_name(label_key)
    # TODO: make this process parallel
    # Unboxing TFRecord files and interleave them with sequential process
    tf_dataset = tf.data.Dataset.list_files(file_pattern, shuffle=False)
    tf_dataset = tf_dataset.interleave(
        lambda x: tf.data.TFRecordDataset(x, compression_type="GZIP")
    )
    # Decode record bytes
    tf_dataset = tf_dataset.map(
        lambda x: tf.io.parse_single_example(x, transformed_feature_spec)
    )
    # Note: the batch size does not impact the training of TF Decision Forest
    tf_dataset = tf_dataset.batch(batch_size=batch_size)
    tf_dataset = tf_dataset.map(lambda x: (x, x.pop(transformed_label)))
    # Seems to provide a small (measured as ~4% on a 32k rows dataset) speed-up
    tf_dataset = tf_dataset.prefetch(tf.data.AUTOTUNE)
    return tf_dataset


def input_fn_v2(
    file_pattern: List[str],
    data_accessor: tfx.components.DataAccessor,
    tf_transform_output: tft.TFTransformOutput,
    batch_size: int,
    label_key: str,
) -> tf.data.Dataset:
    """Generates a dataset (features and label) for training and tuning process.

    Args:
        file_pattern: list of paths or patterns of input tfrecord files
        data_accessor: DataAccessor for converting input to RecordBatch
        tf_transform_output: data schema to load the dataset from TFRecord
            data structures generated by Transform component
        batch_size: representing the number of consecutive elements of returned
            dataset to combine in a single batch
        label_key: feature key of dataset for label (target feature)

    Returns:
        A dataset that contains (features, indices) tuple where features is a
            dictionary of Tensors, and indices is a single Tensor of label indices.
    """

    # transformed_feature_spec = sqz_feature_spec_from_tfm_output(tf_transform_output)
    transformed_feature_spec = tf_transform_output.transformed_feature_spec().copy()
    schema = tft.tf_metadata.schema_utils.schema_from_feature_spec(
        transformed_feature_spec
    )

    return data_accessor.tf_dataset_factory(
        file_pattern,
        tfxio.TensorFlowDatasetOptions(
            # Based on TF-DF ceveats epochs=1 and should not to be shuffled
            num_epochs=1,
            shuffle=False,
            batch_size=batch_size,
            label_key=transformed_name(label_key),
        ),
        schema=schema,
    )


def input_fn_v1(
    file_pattern: List[str],
    tf_transform_output: tft.TFTransformOutput,
    batch_size: int,
    label_key: str,
) -> tf.data.Dataset:
    """Generates a dataset (features and label) for training and tuning process.

    Args:
        file_pattern: list of paths or patterns of input tfrecord files
        tf_transform_output: data schema to load the dataset from TFRecord
            data structures generated by Transform component
        batch_size: representing the number of consecutive elements of
            returned dataset to combine in a single batch
        label_key: feature key of dataset for label (target feature)

    Returns:
        A dataset that contains (features, indices) tuple where features is a
            dictionary of Tensors, and indices is a single Tensor of label indices.
    """

    # transformed_feature_spec = sqz_feature_spec_from_tfm_output(tf_transform_output)
    transformed_feature_spec = tf_transform_output.transformed_feature_spec().copy()
    # See: https://www.tensorflow.org/api_docs/python/tf/data/experimental/make_batched_features_dataset # noqa: E501
    dataset = tf.data.experimental.make_batched_features_dataset(
        file_pattern=file_pattern,
        batch_size=batch_size,
        features=transformed_feature_spec,
        reader=_gzip_reader_fn,
        label_key=transformed_name(label_key),
        # Keep elements (w/o shuffle) of each feature even though the order changed
        # The effect will be activated when num_epochs > 1
        shuffle=False,
        # Length data is n * num_data / batch_size (repeated n-epochs)
        # Num_epoch must be equals to 1 for training / tuning (based on TF-DF ceveats)
        num_epochs=1,
    )

    return dataset
