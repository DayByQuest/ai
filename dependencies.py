# dependencies.py

from model.model import classifier

class ClassifyModel:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls._load_model()
            print("AI Model Loaded")
        return cls._instance

    @staticmethod
    def _load_model():
        # 모델 로드 로직
        model = classifier()
        return model

def get_model():
    return ClassifyModel.get_instance()