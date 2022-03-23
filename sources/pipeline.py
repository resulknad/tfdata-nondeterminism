import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
os.environ['TF_CPP_MAX_VLOG_LEVEL'] = '0'
from tensorflow.data.experimental.service import distribute
import time
import tensorflow as tf
from absl import app

#tf.config.optimizer.set_experimental_options({"disable_meta_optimizer": True})

F = 1
@tf.function
def busy_sleep(s):
# time.sleep is not traced properly by autograph
# that's why we do some pointless computation instead
    orig = s
    while s < 2000*F:
        s+=1
    return s + orig-2000*F

# print traced code
# print(tf.autograph.to_code(busy_sleep.python_function))

def make_dataset():
    dataset1 = tf.data.Dataset.from_tensor_slices(list(range(20)))
    dataset2 = tf.data.Dataset.from_tensor_slices(list(range(20)))
    dataset3 = tf.data.Dataset.from_tensor_slices(list(range(20)))
    dataset = tf.data.Dataset.zip((dataset1, dataset2)).map(lambda a,b: a*100+b, deterministic=True)
    dataset = dataset.map(busy_sleep, num_parallel_calls=1, deterministic=True)
    dataset = tf.data.Dataset.zip((dataset, dataset3)).map(lambda a,b: a*100+b, deterministic=True)

    dataset = dataset.apply(distribute(
                                 job_name="test",
#                                 max_outstanding_requests=1,
#                                 max_request_pipelining_per_worker=1,
                                 processing_mode="distributed_epoch", service="grpc://localhost:4444"))
    return dataset


def main(argv):
    del argv

    dataset = make_dataset()

    def process_epoch(dataset):
        options = tf.data.Options()
        options.experimental_deterministic = True
        dataset = dataset.with_options(options)
        tf.config.experimental.enable_op_determinism()
        res = []
        for x in dataset:
            res.append(x.numpy())
        return res

    for _ in range(100):
        start = time.time()

        print(sorted(process_epoch(dataset)))
        end = time.time()
        print('Epoch took: {}'.format(end - start))

if __name__ == '__main__':
    app.run(main)
