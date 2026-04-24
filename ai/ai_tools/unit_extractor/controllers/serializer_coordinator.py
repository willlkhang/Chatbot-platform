from domain import TextData

class Serializer():
    
    def __init__(self,*serializers):
        self.serializers = serializers
    
    def run(self, data : list[TextData]):
        
        
        for save_path, serialize in self.serializers:
            
            print(f'serializing as {save_path}...')
            serialize(data, save_path)
        
        