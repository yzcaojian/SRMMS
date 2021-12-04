import tensorflow as tf
import numpy as np
import time
import matplotlib.pyplot as plt

"""
-*- coding: utf-8 -*- 
@Project: disk_failure_prediction
@Description: 训练一级健康度模型
@Time : 2021/12/3 14:25
@Author : cao jian
"""

train_data = np.load('../train_data.npy')
train_label = np.load('../train_label.npy')
test_data = np.load('../test_data.npy')
test_label = np.load('../test_label.npy')

# Parameters
epochs = 2000
initial_learning_rate = 0.001
# learning_rate = tf.Variable(0.01, dtype=tf.float32)  # 迭代修改学习率
batch_size = 300
display_step = 200

# Network Parameters
n_input = np.shape(train_data)[2]  # 9
n_steps = np.shape(train_data)[1]  # 20
n_hidden = 128
n_classes = 6


def shuffle_in_unison_scary(a, b):
    rng_state = np.random.get_state()
    np.random.shuffle(a)
    np.random.set_state(rng_state)
    np.random.shuffle(b)
    return a, b


train_data, train_label = shuffle_in_unison_scary(train_data, train_label)

print("prepare for data")
print(train_data.shape)
print(train_label.shape)
# print(train_length.shape)
print("data is ok")

# define the nerual network
# Define weights
weights = {
    'in': tf.Variable(tf.random_uniform([n_input, n_hidden])),
    'out': tf.Variable(tf.random.normal([n_hidden, n_classes]))
}
biases = {
    'in': tf.Variable(tf.random_uniform([n_hidden])),
    'out': tf.Variable(tf.random.normal([n_classes]))
}


def mulitGRU(x):
    x = tf.unstack(x, num=n_steps, axis=1)

    # 可以看做3个隐藏层
    stacked_rnn = []
    for i in range(2):
        stacked_rnn.append(tf.contrib.rnn.GRUCell(num_units=n_hidden))

        # 多层RNN的实现 例如cells=[cell1,cell2]，则表示一共有两层，数据经过cell1后还要经过cell2
    grucell = tf.contrib.rnn.MultiRNNCell(cells=stacked_rnn)
    # 静态rnn函数传入的是一个张量list  每一个元素都是一个(batch_size,n_input)大小的张量
    outputs, states = tf.contrib.rnn.static_rnn(cell=grucell, inputs=x, dtype=tf.float32)

    # 输出层
    outputs = outputs[-1]
    output = tf.matmul(outputs, weights['out']) + biases['out']
    return output


# Define loss and optimizer
def trainGRU(initial_learning_rate):
    global_step = tf.Variable(0, trainable=False)
    learning_rate = tf.compat.v1.train.exponential_decay(initial_learning_rate, global_step=global_step,
                                                         decay_steps=5000, decay_rate=0.90)
    add_global = global_step.assign_add(1)
    # tf Graph input
    x = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, n_steps, n_input])
    y = tf.compat.v1.placeholder(dtype=tf.float32, shape=[None, n_classes])

    pred = mulitGRU(x)

    # define optimizer
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=pred))
    optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate).minimize(cost)
    # optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    # Evaluate model_learning
    correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
    train_acc = []
    train_loss = []

    init = tf.compat.v1.global_variables_initializer()
    print("start training")
    config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=15)
    with tf.compat.v1.Session(config=config) as sess:
        sess.run(init)
        true_epochs = 2000
        for epoch in range(epochs):
            step = 1
            preb = epoch % (len(train_data) % batch_size)
            while preb + batch_size <= len(train_data):
                if epoch < 3000:
                    acc, _, loss, _, lr = sess.run([accuracy, optimizer, cost, add_global, learning_rate],
                                                   feed_dict={x: train_data[preb:batch_size + preb, :, :],
                                                              y: train_label[preb:batch_size + preb, :]})
                else:  # 3000步后不要更改学习率了
                    acc, _, loss, lr = sess.run([accuracy, optimizer, cost, learning_rate],
                                                feed_dict={x: train_data[preb:batch_size + preb, :, :],
                                                           y: train_label[preb:batch_size + preb, :]})

                step += 1
                preb += batch_size
            train_acc.append(acc)
            train_loss.append(loss)
            print("-------------------------------------------------------------------------------", lr)
            print('Epoch', epoch + 1, 'completed out of', epochs, 'loss:', loss, 'accuracy', acc)
            test_accuracy = sess.run(accuracy, feed_dict={x: test_data[300:600, :, :], y: test_label[300:600, :]})
            print("test_accuracy", test_accuracy)
            if test_accuracy > 0.85 and acc > 0.98:
                print("测试集精度超过85%，提前终止")
                true_epochs = epoch + 1
                break
            if epoch % 10 == 0:
                shuffle_in_unison_scary(train_data, train_label)  # 每个epoch都对数据集重新打乱一次
        print("Optimization Finished!")
        print("model_save: ", saver.save(sess, './model_learning/hdd_GRU_model.ckpt'))
        # model_learning:  test accuracy:0.820   参数： lr=0.001, 每5000步衰减10%，batch_size:300,epoch:2000, simpleGRU

        # Calculate accuracy for test data
        clock = time.clock()
        test_acc = []
        step = 1
        preb = 0
        # 优化：测试集没有利用完全
        while step * batch_size <= len(test_data):
            acc, loss = sess.run([accuracy, cost], feed_dict={x: test_data[preb:batch_size + preb, :, :],
                                                              y: test_label[preb:batch_size + preb, :]})
            test_acc.append(acc)
            print("Testing Accuracy:", acc, ", loss:", loss)
            preb += batch_size
            step += 1
        print("average test accuracy: ", np.mean(test_acc))
        print("Execution time :%s" % (time.clock() - clock))

    t = np.arange(true_epochs)

    plt.figure(figsize=(6, 6))
    plt.plot(t, np.array(train_loss), 'r-')

    plt.xlabel("iteration")
    plt.ylabel("Loss")
    # plt.legend(['train', 'validation'], loc='upper right')
    plt.show()

    plt.figure(figsize=(6, 6))
    plt.plot(t, np.array(train_acc))
    plt.xlabel("iteration")
    plt.ylabel("Accuray")
    plt.show()


trainGRU(initial_learning_rate)
