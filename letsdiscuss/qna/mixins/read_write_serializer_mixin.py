
class ReadWriteSerializerMixin:

  read_serializer_class, write_serializer_class = None, None

  def get_serializer_class(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
      return self.get_write_serializer_class()
    return self.get_read_serializer_class()


  def get_read_serializer_class(self):
    assert self.read_serializer_class is not None, (f'{self.__class__.__name__} should either include a `read_serializer_class` attribute, or override the `get_read_serializer_class()` method.')
    return self.read_serializer_class


  def get_write_serializer_class(self):
    assert self.write_serializer_class is not None, (f'{self.__class__.__name__} should either include a `write_serializer_class` attribute, or override the `get_write_serializer_class()` method.')
    return self.write_serializer_class  