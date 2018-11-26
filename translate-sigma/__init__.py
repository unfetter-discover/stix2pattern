from sigma import parser, config, backends
import yaml

backend_names = ['splunk', 'qradar', 'es-qs']

sigma_config = config.SigmaConfiguration()

def process_sigma(pattern: str, translate=False):
    ret_val = {
        'pattern': pattern
    }

    try:
        parsed = parser.SigmaCollectionParser(pattern, sigma_config)
    except (yaml.parser.ParserError, yaml.scanner.ScannerError, parser.SigmaParseError, parser.SigmaCollectionParseError) as e:
        ret_val['validated'] = False
        return ret_val

    ret_val['validated'] = True

    if translate:
        ret_val['translations'] = []

        selected_backends = []

        for backend_name in backend_names:
            selected_backends.append(backends.getBackend(backend_name)(sigma_config, {'rulecomment': False}))

        results = []

        # This is to prevent the default printing from sigmatools
        def mockPrint(*args, **kwargs):
            if args[1]:
                results.append(args[1])

        for backend in selected_backends:
            backend.output_class.print = mockPrint
            try:
                parsed.generate(backend)
            except Exception as e:
                results.append(None)

        for i in range(0, len(backend_names)):
            if results[i]:
                ret_val['translations'].append({
                    'tool': backend_names[i],
                    'query': results[i]
                })

    return ret_val
