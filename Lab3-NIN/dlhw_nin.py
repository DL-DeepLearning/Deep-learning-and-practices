import keras
import numpy as np
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator, random_shift 
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, AveragePooling2D
from keras.initializers import RandomNormal  
from keras import optimizers
from keras.callbacks import LearningRateScheduler
from keras.layers.normalization import BatchNormalization
from keras import backend as K
from keras.callbacks import Callback

batch_size = 128
num_classes = 10
epochs = 164
img_rows, img_cols = 32, 32
img_channels = 3

data_augmentation = True

log_filepath = r'./logs/dropout0.'

(x_train, y_train), (x_test, y_test) = cifar10.load_data()
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')


def scheduler(epoch):
  learning_rate_init = 0.1
  if epoch >= 81:
    learning_rate_init = 0.01
  if epoch >= 122:
    learning_rate_init = 0.001
  return learning_rate_init

def build_model(dropout):
  model = Sequential()
  
  # Weight initialization
  model.add(Conv2D(192, (5, 5), padding='same', kernel_regularizer=keras.regularizers.l2(0.0001), kernel_initializer=RandomNormal(stddev = 0.01), input_shape=x_train.shape[1:]))
  model.add(Activation('relu'))
  model.add(Conv2D(160, (1, 1)))
  model.add(Activation('relu'))
  model.add(Conv2D(96, (1, 1)))
  model.add(Activation('relu'))
  model.add(MaxPooling2D(pool_size=(3, 3),strides=(2,2),padding = 'same'))
  
  model.add(Dropout(dropout))
  
  model.add(Conv2D(192, (5, 5), padding='same', kernel_regularizer=keras.regularizers.l2(0.0001), kernel_initializer=RandomNormal(stddev = 0.05)))
  model.add(Activation('relu'))
  model.add(Conv2D(192, (1, 1)))
  model.add(Activation('relu'))
  model.add(Conv2D(192, (1, 1)))
  model.add(Activation('relu'))
  model.add(AveragePooling2D(pool_size=(3, 3),strides=(2,2),padding = 'same'))
  
  model.add(Dropout(dropout))
  
  model.add(Conv2D(192, (3, 3), padding='same', kernel_regularizer=keras.regularizers.l2(0.0001), kernel_initializer=RandomNormal(stddev = 0.05)))
  model.add(Activation('relu'))
  model.add(Conv2D(192, (1, 1)))
  model.add(Activation('relu'))
  model.add(Conv2D(10, (1, 1)))
  model.add(Activation('relu'))
  
  #model.add(AveragePooling2D(pool_size=(8, 8),strides=(1,1)))
  model.add(GlobalAveragePooling2D())
  
  #model.add(Flatten())
  model.add(Activation('softmax'))
  
      
  sgd = optimizers.SGD(lr=.1, momentum=0.9, nesterov=True)
  #sgd = optimizers.SGD(lr=.1, nesterov=False)
  model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
  return model

class SGDLearningRateTracker(Callback):
    def on_epoch_end(self, epoch, logs={}):
        optimizer = self.model.optimizer
        lr = K.eval(optimizer.lr * (1. / (1. + optimizer.decay * optimizer.iterations)))
        print('\nLR: {:.6f}\n'.format(lr))
        
def main():

  # Data preprocessing
  color_r = np.sum(x_train[:,:,:,0])/(50000.0*32*32)
  color_g = np.sum(x_train[:,:,:,1])/(50000.0*32*32)
  color_b = np.sum(x_train[:,:,:,2])/(50000.0*32*32)
  print(color_r)
  print(color_g)
  print(color_b)
  
  variance_r = np.sqrt(np.sum(np.square(x_train[:,:,:,0] - color_r))/(50000.0*32*32-1)) 
  variance_g = np.sqrt(np.sum(np.square(x_train[:,:,:,1] - color_g))/(50000.0*32*32-1)) 
  variance_b = np.sqrt(np.sum(np.square(x_train[:,:,:,2] - color_b))/(50000.0*32*32-1)) 
  print(variance_r)
  print(variance_g)
  print(variance_b)

  x_train[:,:,:,0] = (x_train[:,:,:,0] - color_r) / variance_r
  x_train[:,:,:,1] = (x_train[:,:,:,1] - color_g) / variance_g
  x_train[:,:,:,2] = (x_train[:,:,:,2] - color_b) / variance_b

  color_r = np.sum(x_test[:,:,:,0])/(10000.0*32*32)
  color_g = np.sum(x_test[:,:,:,1])/(10000.0*32*32)
  color_b = np.sum(x_test[:,:,:,2])/(10000.0*32*32)
  print(color_r)
  print(color_g)
  print(color_b)  

  variance_r = np.sqrt(np.sum(np.square(x_test[:,:,:,0] - color_r))/(10000.0*32*32-1))  
  variance_g = np.sqrt(np.sum(np.square(x_test[:,:,:,1] - color_g))/(10000.0*32*32-1))  
  variance_b = np.sqrt(np.sum(np.square(x_test[:,:,:,2] - color_b))/(10000.0*32*32-1))   
  print(variance_r)
  print(variance_g)
  print(variance_b)

  x_test[:,:,:,0] = (x_test[:,:,:,0] - color_r) / variance_r
  x_test[:,:,:,1] = (x_test[:,:,:,1] - color_g) / variance_g
  x_test[:,:,:,2] = (x_test[:,:,:,2] - color_b) / variance_b

  #x_train /= 255
  #x_test /= 255
  dropout = 0.0
  for i in range(1,10):
    log_file = log_filepath + str(i)
    print(log_file)
    dropout += 0.1
    print(dropout)
    model = build_model(dropout)
    tb_cb = keras.callbacks.TensorBoard(log_dir=log_file, histogram_freq=0)
    change_lr = LearningRateScheduler(scheduler)
    #cbks = [change_lr,tb_cb,SGDLearningRateTracker()]
    cbks = [change_lr,tb_cb]
    if not data_augmentation:
        print('Not using data augmentation.')
        model.fit(x_train, y_train,
                  batch_size=batch_size,
                  epochs=epochs,
                  callbacks=cbks,
                  validation_data=(x_test, y_test),
                  shuffle=True)
    else:
        print('Using real-time data augmentation.')
        datagen = ImageDataGenerator(horizontal_flip=True,
              width_shift_range=0.125,height_shift_range=0.125,fill_mode='constant',cval=0.)
        datagen.fit(x_train)
        model.fit_generator(datagen.flow(x_train, y_train,batch_size=batch_size),
                            steps_per_epoch=391,
                            epochs=epochs,
                            callbacks=cbks,
                            validation_data=(x_test, y_test))
        #model.save('data_augmentation.h5')

if __name__ == '__main__':
    main()