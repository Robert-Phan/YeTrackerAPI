import typing
import pprint

__all__ = [
    'Row', 'Range'
]

type Row = list[str]
type Range = list[Row]

def add_repr[T](cls: type[T]):
    """Decorator that adds a simple __repr__ method."""
    def get_obj_repr(obj):
        obj_repr = repr(obj)

        if not getattr(obj, '__repr_special', False):
            return obj_repr

        repr_by_line = obj_repr.splitlines()
        
        for i in range(len(repr_by_line)):
            if i == 0:
                continue
            
            line = repr_by_line[i]
            line = '    ' + line
            repr_by_line[i] = line

        return '\n'.join(repr_by_line)

    def __repr__(self: T):
        setattr(self, '__repr_special', True)

        attributes: list[str] = []

        for attr, obj in self.__dict__.items():
            if attr[0] == '_':
                continue

            obj_repr = get_obj_repr(obj)

            attr_line = f'    {attr}={obj_repr}'
            attributes.append(attr_line)
        
        attributes_string = ',\n'.join(attributes)

        result = f'{cls.__name__}(\n' \
                + attributes_string \
                + '\n)'

        return result

    cls.__repr__ = __repr__
    return cls