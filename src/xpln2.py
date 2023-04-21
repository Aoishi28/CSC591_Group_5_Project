from sklearn.ensemble import RandomForestClassifier

class XPLN2:
    def __init__(self, best, rest):
        self.best = best
        self.rest = rest
        self.data = None

    def prepare_data(self):
        X_best = []
        y_best = []
        X_rest = []
        y_rest = []
        X_test = []

        for row in self.best.rows:
            X_best.append([row.cells[col.at] for col in self.best.cols.x])
            y_best.append('best')

        for row in self.rest.rows:
            X_rest.append([row.cells[col.at] for col in self.rest.cols.x])
            y_rest.append('rest')

        for row in self.data.rows:
            X_test.append([row.cells[col.at] for col in self.data.cols.x])

        return X_best, y_best, X_rest, y_rest, X_test

    def train_random_forest(self, X_train, y_train):
        clf = RandomForestClassifier(random_state=0)
        clf.fit(X_train, y_train)
        return clf

    def predict_classes(self, clf, X_test):
        best_preds = []
        rest_preds = []

        for idx, row in enumerate(X_test):
            pred = clf.predict([row])

            if pred == "best":
                best_preds.append(self.data.rows[idx])
            else:
                rest_preds.append(self.data.rows[idx])

        return best_preds, rest_preds

    def random_forest(self, data):
        self.data = data
        X_best, y_best, X_rest, y_rest, X_test = self.prepare_data()
        X_train = X_best + X_rest
        y_train = y_best + y_rest
        clf = self.train_random_forest(X_train, y_train)
        best_preds, rest_preds = self.predict_classes(clf, X_test)
        return best_preds, rest_preds
