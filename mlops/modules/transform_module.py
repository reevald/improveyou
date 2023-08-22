import os

import tensorflow as tf
import tensorflow_data_validation as tfdv

# Get Features and The Type
path_schema = f"{os.environ['PATH_SCHEMA']}/schema.pbtxt"
schema = tfdv.load_schema_text(path_schema)
# TYPE_UNKNOWN = 0; BYTES = 1; INT = 2; FLOAT = 3; STRUCT = 4;
# See: https://github.com/tensorflow/metadata/blob/c30ecb401ee2ee67dda5ec450d9e44f24f828803/tensorflow_metadata/proto/v0/schema.proto#L697 # noqa: E501
FEATURES_TYPE = {f.name: f.type for f in schema.feature}


# Feature names matter
# The suffix will help distinguish whether errors are originating from input or output
# Prevent us from accidentally using a nontransformed feature in our actual model
def transformed_name(key):
    """Renaming transformed features"""
    return key + "_xf"


def preprocessing_fn(inputs):
    """Preprocess input features into transformed features by TensorFlow operations.

    Args:
        inputs: map from feature keys to raw features (ingested raw data)
        [dict of Tensors/SparseTensors]

    Return:
        outputs: map from feature keys to transformed features
        [dict of Tensors/SparseTensors]
    """

    # Consider the data types
    # TFT limits the data types of the output features.
    # It exports all preprocessed features as either tf.string, tf.float32, or tf.int64
    outputs = {}
    for name, type in FEATURES_TYPE.items():
        # Since the types of the data are int (based on SchemaGen output - previously)
        if type == 2:
            dtype = tf.int64

        # Change input dimension shape from [None, 1] to [None,] (consider input TF-DF)
        # Alternative: we can move this step into last preprocessing
        # on signature of the model and do squeeze feature spec on input_fn
        # Note: both (this and the alternative) still have bug on TFMA (F1-Score metric)
        outputs[transformed_name(name)] = tf.cast(
            x=tf.reshape(inputs[name], shape=[tf.shape(inputs[name])[0]]), dtype=dtype
        )

    return outputs
