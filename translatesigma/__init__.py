from sigma import parser, config, backends
from typing import Dict
import yaml

backend_names = ['splunk', 'qradar', 'es-qs']

sigma_config = config.SigmaConfiguration()


def process_sigma(pattern: str, translate=False) -> Dict[str, any]:
    """
    :param pattern: str (stringified SIGMA)
    :param translate: boolean (default False)
    :return: { pattern: str, validated: bool, message?: str, translations?: [{tool: str, query: str}] }

    Validates stringified YAML as SIGMA.
    If it is valid SIGMA and translate is set to True,
    it will translate it to various backends' syntax
    """
    ret_val = {
        'pattern': pattern
    }

    try:
        parsed = parser.SigmaCollectionParser(pattern, sigma_config)
    except (yaml.parser.ParserError, yaml.scanner.ScannerError, yaml.YAMLError) as e:
        ret_val['message'] = 'Not valid YAML'
        ret_val['validated'] = False
        return ret_val
    except (parser.SigmaParseError, parser.SigmaCollectionParseError) as e:
        ret_val['message'] = 'Not valid Sigma'
        ret_val['validated'] = False
        return ret_val
    except Exception as e:
        ret_val['message'] = 'An unknown error occured'
        ret_val['validated'] = False
        return ret_val

    ret_val['validated'] = True

    if translate:
        ret_val['translations'] = []

        selected_backends = []

        for backend_name in backend_names:
            selected_backends.append(backends.getBackend(backend_name)(sigma_config, {'rulecomment': False}))

        results = []

        # This is to prevent the default printing behavior from sigmatools
        def wrap_mock_print(backend):
            def mock_print(*args, **kwargs):
                if args[1]:
                    results.append({'tool': backend.identifier, 'query': args[1]})

            return mock_print

        for backend in selected_backends:
            backend.output_class.print = wrap_mock_print(backend)
            try:
                parsed.generate(backend)
            except Exception as e:
                # Usually: Aggregations not implemented for this backend
                pass

        if len(results):
            ret_val['translations'] = results

    return ret_val
