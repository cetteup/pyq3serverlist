import unittest
from dataclasses import dataclass
from typing import List, Optional

from pyq3serverlist import PyQ3SLError, Server


class ServerTest(unittest.TestCase):
    def test_parse_response(self):
        @dataclass
        class ParseResponseTestCase:
            name: str
            data: bytes
            expected: Optional[dict] = None
            wantErrContains: Optional[str] = None

        tests: List[ParseResponseTestCase] = [
            ParseResponseTestCase(
                name='parses response packet without players',
                data=b'\xff\xff\xff\xffstatusResponse\n'
                     b'\\bot_minplayers\\2\\dmflags\\0\\fraglimit\\0\\g_gametype\\0\\mapname\\q3dm17\\protocol\\68'
                     b'\\sv_allowDownload\\1\\sv_dlRate\\100\\sv_dlURL\\http://www.tigerhareram.cz/files/Quake3'
                     b'\\sv_hostname\\! ^2Tigers DM17^7 baseq3\\sv_maxRate\\25000\\sv_maxclients\\20\\sv_minRate\\0'
                     b'\\sv_pure\\0\\timelimit\\10\\version\\Q3 1.32e linux-x86_64 Sep 14 2018'
                     b'\\Info\\1Z\t\t  \t2 2 \t1Z 1Z \t\\Uptime\\1:58:22\\capturelimit\\0\\g_blueTeam\\^4BLUE'
                     b'\\g_needpass\\0\\g_redTeam\\^1RED\\gamename\\excessiveplus\\roundlimit\\0\\sv_punkbuster\\0'
                     b'\\xp_date\\Jun 20 2014'
                     b'\\xp_version\\2.3 baseq3.cfg c32d0ef5a59f6619bc974fc3228608e1 Quake III Arena v1.32\n',
                expected={
                    'ip': '127.0.0.1',
                    'port': 27960,
                    'bot_minplayers': '2',
                    'dmflags': '0',
                    'fraglimit': '0',
                    'g_gametype': '0',
                    'mapname': 'q3dm17',
                    'protocol': '68',
                    'sv_allowDownload': '1',
                    'sv_dlRate': '100',
                    'sv_dlURL': 'http://www.tigerhareram.cz/files/Quake3',
                    'sv_hostname': '! Tigers DM17 baseq3',
                    'sv_maxRate': '25000',
                    'sv_maxclients': '20',
                    'sv_minRate': '0',
                    'sv_pure': '0',
                    'timelimit': '10',
                    'version': 'Q3 1.32e linux-x86_64 Sep 14 2018',
                    'Info': '1Z\t\t  \t2 2 \t1Z 1Z \t',
                    'Uptime': '1:58:22',
                    'capturelimit': '0',
                    'g_blueTeam': 'BLUE',
                    'g_needpass': '0',
                    'g_redTeam': 'RED',
                    'gamename': 'excessiveplus',
                    'roundlimit': '0',
                    'sv_punkbuster': '0',
                    'xp_date': 'Jun 20 2014',
                    'xp_version': '2.3 baseq3.cfg c32d0ef5a59f6619bc974fc3228608e1 Quake III Arena v1.32',
                    'players': []
                }
            ),
            ParseResponseTestCase(
                name='parses response packet with players',
                data=b'\xff\xff\xff\xffstatusResponse\n\\sv_maxclients\\32\\sv_privateClients\\0\\version'
                     b'\\Q3 1.32c linux-i386 May  8 2009\\com_protocol\\71\\protocol\\68\\dmflags\\0\\fraglimit\\20'
                     b'\\timelimit\\20\\g_gametype\\4\\mapname\\q3ctf1\\sv_hostname\\Thunder CTF\\sv_minRate\\0'
                     b'\\sv_maxRate\\25000\\sv_minPing\\0\\sv_maxPing\\0\\sv_floodProtect\\1\\sv_allowDownload\\1'
                     b'\\bot_minplayers\\1\\ Administrator\\Jordon\\ E-mail\\admin@matchlessgaming.com'
                     b'\\ Location\\San Jose, CA\\ Website\\matchlessgaming.com\\capturelimit\\8\\gamename\\baseq3'
                     b'\\g_maxGameClients\\0\\g_needpass\\0\\Score_Time\\13:56\\Score_Blue\\1\\Score_Red\\2\n'
                     b'0 64 "^1Fo"\n'
                     b'0 12 "MonyMakr"\n'
                     b'0 28 "Wit^1Dvil"\n'
                     b'0 17 "^2Kaza"\n'
                     b'6 0 "Uriel"\n'
                     b'0 75 "^5Doo Doo"\n'
                     b'0 56 "^3styv"\n'
                     b'0 85 "YoPaPa"\n'
                     b'14 0 "Sorlag"\n'
                     b'0 11 "Trodat"\n'
                     b'14 11 "SiLNT"\n'
                     b'0 75 "crazy"\n'
                     b'0 29 "dan"\n'
                     b'0 107 "Jos"\n',
                expected={
                    'ip': '127.0.0.1',
                    'port': 27960,
                    'sv_maxclients': '32',
                    'sv_privateClients': '0',
                    'version': 'Q3 1.32c linux-i386 May  8 2009',
                    'com_protocol': '71',
                    'protocol': '68',
                    'dmflags': '0',
                    'fraglimit': '20',
                    'timelimit': '20',
                    'g_gametype': '4',
                    'mapname': 'q3ctf1',
                    'sv_hostname': 'Thunder CTF',
                    'sv_minRate': '0',
                    'sv_maxRate': '25000',
                    'sv_minPing': '0',
                    'sv_maxPing': '0',
                    'sv_floodProtect': '1',
                    'sv_allowDownload': '1',
                    'bot_minplayers': '1',
                    ' Administrator': 'Jordon',
                    ' E-mail': 'admin@matchlessgaming.com',
                    ' Location': 'San Jose, CA',
                    ' Website': 'matchlessgaming.com',
                    'capturelimit': '8',
                    'gamename': 'baseq3',
                    'g_maxGameClients': '0',
                    'g_needpass': '0',
                    'Score_Time': '13:56',
                    'Score_Blue': '1',
                    'Score_Red': '2',
                    'players': [
                        {'frags': 0, 'ping': 64, 'name': 'Fo', 'colored_name': '^1Fo'},
                        {'frags': 0, 'ping': 12, 'name': 'MonyMakr', 'colored_name': 'MonyMakr'},
                        {'frags': 0, 'ping': 28, 'name': 'WitDvil', 'colored_name': 'Wit^1Dvil'},
                        {'frags': 0, 'ping': 17, 'name': 'Kaza', 'colored_name': '^2Kaza'},
                        {'frags': 6, 'ping': 0, 'name': 'Uriel', 'colored_name': 'Uriel'},
                        {'frags': 0, 'ping': 75, 'name': 'Doo Doo', 'colored_name': '^5Doo Doo'},
                        {'frags': 0, 'ping': 56, 'name': 'styv', 'colored_name': '^3styv'},
                        {'frags': 0, 'ping': 85, 'name': 'YoPaPa', 'colored_name': 'YoPaPa'},
                        {'frags': 14, 'ping': 0, 'name': 'Sorlag', 'colored_name': 'Sorlag'},
                        {'frags': 0, 'ping': 11, 'name': 'Trodat', 'colored_name': 'Trodat'},
                        {'frags': 14, 'ping': 11, 'name': 'SiLNT', 'colored_name': 'SiLNT'},
                        {'frags': 0, 'ping': 75, 'name': 'crazy', 'colored_name': 'crazy'},
                        {'frags': 0, 'ping': 29, 'name': 'dan', 'colored_name': 'dan'},
                        {'frags': 0, 'ping': 107, 'name': 'Jos', 'colored_name': 'Jos'}
                    ]
                }
            ),
            ParseResponseTestCase(
                name='parses ioquake response packet',
                data=b'\xff\xff\xff\xffstatusResponse\n\\fs_cdn\\84.252.132.60:9000\\server_gameplay\\VQ3\\sv_fps\\30'
                     b'\\g_maxGameClients\\0\\sv_dlURL\\http://84.252.132.60:8000\\sv_allowDownload\\1'
                     b'\\sv_floodProtect\\0\\sv_maxPing\\0\\sv_minPing\\0\\sv_dlRate\\2000\\sv_maxRate\\30000'
                     b'\\sv_minRate\\0\\sv_maxclients\\24\\sv_hostname\\The Quake CTF (VQ3)\\sv_privateClients\\0'
                     b'\\g_gametype\\4\\timelimit\\15\\fraglimit\\25\\dmflags\\0\\version'
                     b'\\ioq3 1.36_GIT_3326551a-2022-07-26 linux-x86_64 Aug  4 2022\\com_gamename\\Quake3Arena'
                     b'\\com_protocol\\71\\mapname\\13camp\\fs_manifest\\baseq3/13camp.pk3@319779252@6099774\n '
                     b'baseq3/pak100.pk3@2388798635@16506992\n baseq3/pak101.pk3@2206768903@2657563\n '
                     b'baseq3/pak102.pk3@2076841188@3024290\n cpma/z-cpma-pak152.pk3@3054920672@8135165\n '
                     b'linuxq3ademo-1.11-6.x86.gz.sh@857908472@49289300\n '
                     b'linuxq3apoint-1.32b-3.x86.run@296843703@30923961\n '
                     b'\\game\\CPMA\\gamename\\cpma\\gamedate\\Apr 03 2019\\gameversion\\1.52\\sv_arenas\\1'
                     b'\\Score_Time\\11:12\\Score_Red\\1\\Score_Blue\\2\\Players_Red\\1 4 5 8 9 '
                     b'\\Players_Blue\\2 7 10 11 12 \\GTV_CN\\1\\g_needpass\\0\\mode_current\\PUBCTF\n'
                     b'10 33 "^z0^7UnnamedPlayer"\n'
                     b'18 31 "^z1^7^oAndreas"\n'
                     b'18 85 "^z2^7UnnamedPlayer"\n'
                     b'14 61 "^z3^7^ox^y736C"\n'
                     b'2 285 "^z4^7UnnamedPlayer"\n'
                     b'0 55 "^z5^7UnnamedPlayer"\n'
                     b'16 31 "^z6^7UnnamedPlayer"\n'
                     b'3 41 "^z7^7UnnamedPlayer"\n'
                     b'28 19 "^z10^7tom"\n'
                     b'0 37 "^z11^7UnnamedPlayer"\n'
                     b'9 39 "^z13^7UnnamedPlayer"\n'
                     b'7 210 "^z14^7chilote"\n',
                expected={
                    'ip': '127.0.0.1',
                    'port': 27960,
                    'fs_cdn': '84.252.132.60:9000',
                    'server_gameplay': 'VQ3',
                    'sv_fps': '30',
                    'g_maxGameClients': '0',
                    'sv_dlURL': 'http://84.252.132.60:8000',
                    'sv_allowDownload': '1',
                    'sv_floodProtect': '0',
                    'sv_maxPing': '0',
                    'sv_minPing': '0',
                    'sv_dlRate': '2000',
                    'sv_maxRate': '30000',
                    'sv_minRate': '0',
                    'sv_maxclients': '24',
                    'sv_hostname': 'The Quake CTF (VQ3)',
                    'sv_privateClients': '0',
                    'g_gametype': '4',
                    'timelimit': '15',
                    'fraglimit': '25',
                    'dmflags': '0',
                    'version': 'ioq3 1.36_GIT_3326551a-2022-07-26 linux-x86_64 Aug  4 2022',
                    'com_gamename': 'Quake3Arena',
                    'com_protocol': '71',
                    'mapname': '13camp',
                    'fs_manifest': 'baseq3/13camp.pk3@319779252@6099774\n '
                                   'baseq3/pak100.pk3@2388798635@16506992\n '
                                   'baseq3/pak101.pk3@2206768903@2657563\n '
                                   'baseq3/pak102.pk3@2076841188@3024290\n '
                                   'cpma/z-cpma-pak152.pk3@3054920672@8135165\n '
                                   'linuxq3ademo-1.11-6.x86.gz.sh@857908472@49289300\n '
                                   'linuxq3apoint-1.32b-3.x86.run@296843703@30923961\n ',
                    'game': 'CPMA',
                    'gamename': 'cpma',
                    'gamedate': 'Apr 03 2019',
                    'gameversion': '1.52',
                    'sv_arenas': '1',
                    'Score_Time': '11:12',
                    'Score_Red': '1',
                    'Score_Blue': '2',
                    'Players_Red': '1 4 5 8 9 ',
                    'Players_Blue': '2 7 10 11 12 ',
                    'GTV_CN': '1',
                    'g_needpass': '0',
                    'mode_current': 'PUBCTF',
                    'players': [
                        {'frags': 10, 'ping': 33, 'name': '0UnnamedPlayer', 'colored_name': '^z0^7UnnamedPlayer'},
                        {'frags': 18, 'ping': 31, 'name': '1Andreas', 'colored_name': '^z1^7^oAndreas'},
                        {'frags': 18, 'ping': 85, 'name': '2UnnamedPlayer', 'colored_name': '^z2^7UnnamedPlayer'},
                        {'frags': 14, 'ping': 61, 'name': '3x736C', 'colored_name': '^z3^7^ox^y736C'},
                        {'frags': 2, 'ping': 285, 'name': '4UnnamedPlayer', 'colored_name': '^z4^7UnnamedPlayer'},
                        {'frags': 0, 'ping': 55, 'name': '5UnnamedPlayer', 'colored_name': '^z5^7UnnamedPlayer'},
                        {'frags': 16, 'ping': 31, 'name': '6UnnamedPlayer', 'colored_name': '^z6^7UnnamedPlayer'},
                        {'frags': 3, 'ping': 41, 'name': '7UnnamedPlayer', 'colored_name': '^z7^7UnnamedPlayer'},
                        {'frags': 28, 'ping': 19, 'name': '10tom', 'colored_name': '^z10^7tom'},
                        {'frags': 0, 'ping': 37, 'name': '11UnnamedPlayer', 'colored_name': '^z11^7UnnamedPlayer'},
                        {'frags': 9, 'ping': 39, 'name': '13UnnamedPlayer', 'colored_name': '^z13^7UnnamedPlayer'},
                        {'frags': 7, 'ping': 210, 'name': '14chilote', 'colored_name': '^z14^7chilote'}
                    ]
                }
            ),
            ParseResponseTestCase(
                name='errors for incomplete header',
                data=b'\xff\xff\xff\xff',
                wantErrContains='Server returned invalid packet header'
            ),
            ParseResponseTestCase(
                name='errors for incorrect header',
                data=b'\x00\x00\x00\x00statusResponse\t',
                wantErrContains='Server returned invalid packet header'
            ),
            ParseResponseTestCase(
                name='errors for body not starting with backslash',
                data=b'\xff\xff\xff\xffstatusResponse\nkey\\value\n',
                wantErrContains='Server returned invalid packet body'
            ),
            ParseResponseTestCase(
                name='errors for body containing uneven number of backslashes',
                data=b'\xff\xff\xff\xffstatusResponse\n\\key\\value\\other-key\n',
                wantErrContains='Server returned invalid packet body'
            ),
            ParseResponseTestCase(
                name='errors for body not ending with delimiter',
                data=b'\xff\xff\xff\xffstatusResponse\n\\key\\value',
                wantErrContains='Server returned invalid packet body'
            )
        ]

        for t in tests:
            # GIVEN
            server = Server('127.0.0.1', 27960)

            if t.wantErrContains is not None:
                # WHEN/THEN
                self.assertRaisesRegex(
                    PyQ3SLError,
                    t.wantErrContains,
                    server.parse_response,
                    t.data
                )
            else:
                # WHEN
                actual = server.parse_response(t.data)

                # THEN
                self.assertDictEqual(t.expected, actual)


if __name__ == '__main__':
    unittest.main()
