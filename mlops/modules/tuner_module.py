import os

import keras_tuner as kt
import tensorflow_transform as tft
import tfx.v1 as tfx
from utils import (
    cm_builder,
    gbtm_builder,
    input_fn_v1,
    input_fn_v2,
    input_fn_v3,
    rfm_builder,
)


def get_hyperparameters():
    """Returns hyperparameters for building model."""
    hp = kt.HyperParameters()
    hp.Fixed("threshold", float(os.environ["BEST_THRESHOLD"]))
    # Define hyperparameters for decision forest
    hp.Int("num_trees", 250, 300, 5, default=250)
    hp.Choice("max_depth", [4, 5, 6], default=5)
    hp.Choice("min_examples", [6, 7, 8], default=6)
    return hp


def tuner_fn(fn_args):
    """Build the tuner using the KerasTuner API.
    Args:
      fn_args: Holds args as name/value pairs.
        - working_dir: working dir for tuning.
        - train_files: List of file paths containing training tf.Example data.
        - eval_files: List of file paths containing eval tf.Example data.
        - train_steps: number of train steps.
        - eval_steps: number of eval steps.
        - schema_path: optional schema of the input data.
        - transform_graph_path: optional transform graph produced by TFT.
    Returns:
      A namedtuple contains the following:
        - tuner: A BaseTuner that will be used for tuning.
        - fit_kwargs: Args to pass to tuner's run_trial function for fitting the
                      model , e.g., the training and validation dataset. Required
                      args depend on the above tuner's implementation.
    """
    # Alternative: you can use transform_graph
    # fn_args.transform_output [Deprecated]
    # use transform_graph_path instead
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_graph_path)
    batch_size = int(os.environ["BATCH_SIZE"])
    label_key = os.environ["LABEL_KEY"]

    if os.environ["INPUT_FN_VERSION"] == "V1":
        train_dataset = input_fn_v1(
            file_pattern=fn_args.train_files,
            tf_transform_output=tf_transform_output,
            batch_size=batch_size,
            label_key=label_key,
        )
        val_dataset = input_fn_v1(
            file_pattern=fn_args.eval_files,
            tf_transform_output=tf_transform_output,
            batch_size=batch_size,
            label_key=label_key,
        )

    if os.environ["INPUT_FN_VERSION"] == "V2":
        train_dataset = input_fn_v2(
            file_pattern=fn_args.train_files,
            data_accessor=fn_args.data_accessor,
            tf_transform_output=tf_transform_output,
            batch_size=batch_size,
            label_key=label_key,
        )
        val_dataset = input_fn_v2(
            file_pattern=fn_args.eval_files,
            data_accessor=fn_args.data_accessor,
            tf_transform_output=tf_transform_output,
            batch_size=batch_size,
            label_key=label_key,
        )

    if os.environ["INPUT_FN_VERSION"] == "V3":
        train_dataset = input_fn_v3(
            file_pattern=fn_args.train_files,
            tf_transform_output=tf_transform_output,
            batch_size=batch_size,
            label_key=label_key,
        )
        val_dataset = input_fn_v3(
            file_pattern=fn_args.eval_files,
            tf_transform_output=tf_transform_output,
            batch_size=batch_size,
            label_key=label_key,
        )

    if os.environ["MODEL_TYPE"] == "RFM":
        model_builder = rfm_builder

    if os.environ["MODEL_TYPE"] == "GBTM":
        model_builder = gbtm_builder

    if os.environ["MODEL_TYPE"] == "CM":
        model_builder = cm_builder

    # Keras Tuner Class
    # see: https://keras.io/api/keras_tuner/
    # - RandomSearch Tuner
    # - GridSearch Tuner
    # - BayesianOptimization Tuner
    # - Hyperband Tuner [Not suitable, epochs-based meanwhile TF-DF epochs=1]
    # - Sklearn Tuner [Not suitable, for sklearn models]

    if os.environ["TUNER_TYPE"] == "RST":
        tuner = kt.RandomSearch(
            hypermodel=model_builder,
            objective=kt.Objective("val_f1_score", "max"),
            max_trials=int(os.environ["MAX_TRIALS"]),
            hyperparameters=get_hyperparameters(),
            # Reloads an existing project of the same name if one is found.
            # Otherwise, overwrites the project.
            overwrite=True,
            directory=fn_args.working_dir,
        )

    if os.environ["TUNER_TYPE"] == "GST":
        tuner = kt.GridSearch(
            hypermodel=model_builder,
            objective=kt.Objective("val_f1_score", "max"),
            max_trials=int(os.environ["MAX_TRIALS"]),
            hyperparameters=get_hyperparameters(),
            overwrite=True,
            directory=fn_args.working_dir,
        )

    if os.environ["TUNER_TYPE"] == "BOT":
        tuner = kt.BayesianOptimization(
            hypermodel=model_builder,
            objective=kt.Objective("val_f1_score", "max"),
            max_trials=int(os.environ["MAX_TRIALS"]),
            hyperparameters=get_hyperparameters(),
            overwrite=True,
            directory=fn_args.working_dir,
        )

    return tfx.components.TunerFnResult(
        tuner=tuner,
        fit_kwargs={"x": train_dataset, "validation_data": val_dataset},
    )
