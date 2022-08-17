import ast
import yaml
import json
import inspect

class Foae:
    def __init__(self, title: str, version: str = '1.0.0') -> None:
        self.spec = {
            'openapi': '3.1.0',
            'info': {
                'title': title,
                'version': version,
            },
            'paths': {}
        }
    
    def parse(self, module: ast.Module, route_filter: callable = None) -> None:
        source = inspect.getsource(module)
        src_ast = ast.parse(source)

        routes = {}
        for node in ast.walk(src_ast):
            if not isinstance(node, ast.FunctionDef):
                continue

            def is_flask_route(decorator: ast.Call) -> bool:
                return isinstance(decorator, ast.Call) and decorator.func.attr == 'route' and isinstance(decorator.args[0], ast.Str)

            decorator = next((decorator for decorator in node.decorator_list if is_flask_route(decorator)), None)
            if not decorator:
                continue

            definition = {}

            # Extract the supported HTTP methods
            for keyword in decorator.keywords:
                if keyword.arg != 'methods':
                    continue

                for value in keyword.value.elts:
                    http_method = value.s.lower()
                    definition[http_method] = {'tags': [node.name]}

            if not definition:
                definition['get'] = { 'tags': [node.name] }
            
            for _, d in definition.items():
                d['response'] = {
                    200: {
                        'description': 'Success'
                    }
                }

            # Store the route definition
            rule = decorator.args[0].s
            if route_filter and not route_filter(rule):
                continue

            rule = rule.replace('<', '{').replace('>', '}')
            routes[rule] = definition

            # Extract the path parameters
            path_params = [part[1:-1] for part in rule.split('/') if part.startswith('{')]
            if not path_params:
                continue
            
            # Get type hint of each parameter
            type_hints = {
                param.arg: self._map_type(param.annotation.id)
                for param in node.args.args + node.args.kwonlyargs + node.args.kw_defaults 
                if isinstance(param.annotation, ast.Name)
            }

            definition['parameters'] = [{
                'name': param,
                'in': 'path',
                'required': True,
                'schema': {
                    'type': type_hints[param]
                }
            } for param in path_params]

            if not definition:
                continue
            
        # Store routes
        for rule, definition in routes.items():
            self.spec['paths'][rule] = definition

    def _map_type(self, t: type) -> str:
        if t == int:
            return 'integer'
        elif t == str:
            return 'string'
        elif t == bool:
            return 'boolean'
        elif t == list:
            return 'array'
        elif t == dict:
            return 'object'
        return 'string'

    def export_as(self, extension: str) -> None:
        file_name = 'openapi.{}'.format(extension)
        with open(file_name, 'w') as f:
            if extension == 'yaml':
                yaml.dump(self.spec, f)
            elif extension == 'json':
                json.dump(self.spec, f)
            else:
                raise ValueError('Unknown extension: {}'.format(extension))
