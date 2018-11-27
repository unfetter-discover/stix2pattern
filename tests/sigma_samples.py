valid_yaml_samples = [
    (
        """fruits:
        - Apple
        - Orange
        - Strawberry
        - Mango""",
        False,
        None
    )
]

invalid_yaml_samples = [
    (
        '{not_yaml: true}',
        False,
        None
    ),
    (
        'something random',
        False,
        None
    )
]

valid_sigma_samples = [
    (
"""title: WSF/JSE/JS/VBA/VBE File Execution
status: experimental
description: Detects suspicious file execution by wscript and cscript
author: Michael Haag
logsource:
    product: windows
    service: sysmon
detection:
    selection:
        EventID: 1
        Image:
            - '*\wscript.exe'
            - '*\cscript.exe'
        CommandLine:
            - '*.jse'
            - '*.vbe'
            - '*.js'
            - '*.vba'
    condition: selection
fields:
    - CommandLine
    - ParentCommandLine
falsepositives:
    - Will need to be tuned. I recommend adding the user profile path in CommandLine if it is getting too noisy.
level: medium""",
        True,
        [
            {
                'tool': 'splunk',
          'query': '(EventID="1" (Image="*\\\\wscript.exe" OR Image="*\\\\cscript.exe") (CommandLine="*.jse" OR CommandLine="*.vbe" OR CommandLine="*.js" OR CommandLine="*.vba"))'
             },
             {
                 'tool': 'qradar',
              'query': "SELECT UTF8(payload) as search_payload from events where ((search_payload ilike '1' and (search_payload ilike '%\\wscript.exe' or search_payload ilike '%\\cscript.exe') and (search_payload ilike '%.jse' or search_payload ilike '%.vbe' or search_payload ilike '%.js' or search_payload ilike '%.vba')))"
             },
             {
                 'tool': 'es-qs',
              'query': '(EventID:"1" AND Image:("*\\\\wscript.exe" "*\\\\cscript.exe") AND CommandLine:("*.jse" "*.vbe" "*.js" "*.vba"))'
             }
        ]
    ),
    (
"""title: Network Scans
description: Detects many failed connection attempts to different ports or hosts
author: Thomas Patzke
logsource:
    category: firewall
detection:
    selection:
        action: denied
    timeframe: 24h
    condition:
        - selection | count(dst_port) by src_ip > 10
        - selection | count(dst_ip) by src_ip > 10
fields:
    - src_ip
    - dst_ip
    - dst_port
falsepositives:
    - Inventarization systems
    - Vulnerability scans
    - Penetration testing activity
level: medium""",
        True,
        [
            {
                'tool': 'splunk',
                'query': '(action="denied") | stats count(dst_port) as val by src_ip | search val > 10'
            },
            {
                'tool': 'qradar',
                'query': '(action="denied") | stats count(dst_ip) as val by src_ip | search val > 10'
            }
        ]
    ),
    (
"""title: Multiple suspicious Response Codes caused by Single Client
description: Detects possible exploitation activity or bugs in a web application
author: Thomas Patzke
logsource:
    category: webserver
detection:
    selection:
        response:
          - 400
          - 401
          - 403
          - 500
    timeframe: 10m
    condition: selection | count() by clientip > 10
fields:
    - client_ip
    - vhost
    - url
    - response
falsepositives:
    - Unstable application
    - Application that misuses the response codes
level: medium""",
        True,
        [
            {
                'tool': 'splunk',
                'query': '((response="400" OR response="401" OR response="403" OR response="500")) | stats count(None) as val by clientip | search val > 10'
            }
        ]
    )
]