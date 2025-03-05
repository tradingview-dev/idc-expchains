from utils import execute_to_file


def korea_handler():
    cmd_line = ["bash", "-c", "curl -s 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'"
                " --data-raw 'code=gRY0jP6rQnfIF4FBiKhU6zCBs%2Fh%2FA%2BJ7QlF9gsIMcSoRtSksuLS7Bnxpl86F7dAOvXfGx9S2U5wgvoxsacATRRtmGtORI4WrGDmruVe6oXtCqUypoW0Lp6SAPP0PhVkgThCTcjIZNPI5lCTubZnhjio6AHXdxc45YVEhz4JdugHPMxvIwHadpQpCGE1HxZAXvTCprTIXuXT9XxFb88awpQ%3D%3D' "
                " | iconv -f EUC-KR"]
    execute_to_file(cmd_line, "korea_local_descriptions.csv")
