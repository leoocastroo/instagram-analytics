from tensorflow import keras


class LogisticRegression():

    def __init__(self):
        self.model = keras.Sequential([
            keras.layers.Input(shape=(3, )),
            keras.layers.Dense(units=1, activation='sigmoid')
        ])

        self.model.compile(optimizer="SGD", loss="binary_crossentropy")

    def load_model(self, model_name):
        self.model.load_weights(f'../weights/{model_name}.h5')

    def save_model(self, model_name):
        self.model.save_weights(f'../weights/{model_name}.h5')

    def train(self, x, y, epochs):
        self.model.fit(x, y, epochs=epochs)

    def predict(self, x):
        pass