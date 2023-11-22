import itertools 
from itertools import repeat
import subprocess
import re
import logging
import datetime as dt
import time

from settings import SERVER_IP, PORT, TEST_DURATION, MESSAGE_SIZES, TEST_TYPES, TCP_ENABLED, CLIENT_IP, TCP_INTERVAL, UDP_INTERVAL


class SockperfTester:
    def __init__(self, running_log, result_log):
        self.command = ["sockperf", "", "-i", SERVER_IP, "-p", str(PORT), "-t", str(TEST_DURATION), "-m", "", "",
        "--client_ip", CLIENT_IP, "--client_port", str(PORT), "--mps=max"]
        self.error_count = 0

        # 로깅 설정
        self.running_log = running_log
        self.result_log = result_log
        self.running_logger = logging.getLogger("RunningLogger")
        self.result_logger = logging.getLogger("ResultLogger")
        
        # Running Logger 설정
        self.running_logger.setLevel(logging.INFO)
        running_logger_handler = logging.FileHandler(self.running_log)
        self.running_logger.addHandler(running_logger_handler)

        # Result Logger 설정
        self.result_logger.setLevel(logging.INFO)
        result_logger_handler = logging.FileHandler(self.result_log)
        self.result_logger.addHandler(result_logger_handler)


    def run_tests(self, iteration):
        # 로깅 설정
        # logging.basicConfig(filename=self.running_log, level=logging.INFO, format="%(message)s")
        
        # 테스트 유형과 메시지 크기의 조합을 반복하여 테스트 실행
        for test_type, message_size in itertools.product(TEST_TYPES, MESSAGE_SIZES):
            # 테스트 유형과 메시지 크기에 따라 명령어 업데이트
            if TCP_ENABLED:
                self.command[10] = "--tcp"
            self.command[1] = test_type
            self.command[9] = str(message_size)

            results = 0.0
            self.error_count = 0

            # 테스트 실행 및 결과 추출
            for index in range(iteration):
                try:                    
                    output = self.run_test()
                    if output:
                        # 실행결과 콘솔출력
                        self.print_result(test_type, message_size, self.command, output, index, self.error_count)  
                        
                        # Error가 없는 경우, 수치확인
                        result = self.extract_result(output, test_type)                        
                        if result:
                            # 결과를 로그 파일에 저장
                            self.log_result(test_type, message_size, result, index, self.error_count)
                            # 반복횟수에 따른 평균 결과계산용
                            results += float(result)
                        # Exception Error 이외 측정이 안된 경우
                        # Ex) Is the server down? , interrupted by timer
                        else:
                            result = 0
                            self.error_count += 1
                            self.log_result(test_type, message_size, result, index, self.error_count)    
                except Exception as e:
                    self.running_logger.error(f"Error executing sockperf command: {str(e)}")
                    print(f"Error executing sockperf command: {str(e)}")

            # Total Avg
            # 반복횟수와 오류횟수가 동일하면 전체 측정 실패
            # 이 경우, total_result 값이 0
            if iteration == self.error_count:
                total_result = 0
            else:
                calculation_counts = iteration - self.error_count
                total_result = round(results / calculation_counts, 2)
            
            self.log_total_avg(test_type, message_size, total_result, iteration, self.error_count, calculation_counts)
            self.print_total_avg(test_type, message_size, total_result, iteration, self.error_count, calculation_counts)


    def run_test(self):
        # sockperf 명령어 실행
        command = " ".join(str(arg) for arg in self.command)
        if TCP_ENABLED:
            time.sleep(TCP_INTERVAL)
        else:
            time.sleep(UDP_INTERVAL)
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            stdout, _ = process.communicate()
            return stdout.decode()
        except Exception as e:
            raise Exception(f"Error executing sockperf command: {str(e)}")

    # output 결과에 throughput, avg-latency 부분 추출
    def extract_result(self, output, test_type):
        pattern = None

        if test_type == "throughput":
            pattern = r"(\d+\.\d+)\s+MBps"
        elif test_type in ["ping-pong", "under-load"]:
            pattern = r"avg-latency=(\d+\.\d+)"

        if pattern:
            match = re.search(pattern, output)
            if match:
                return match.group(1)

        return None


    def log_result(self, test_type, message_size, result, index, error_count):
        self.running_logger.info(f"Server IP: {SERVER_IP}")
        self.running_logger.info(f"Iter-Index: {index}")
        self.running_logger.info(f"Error Count: {error_count}")
        self.running_logger.info(f"Test Type: {test_type}")
        self.running_logger.info(f"Message Size: {message_size}")
        if test_type == "throughput":
            self.running_logger.info(f"Bandwidth(Mbps): {result}")
        else:
            self.running_logger.info(f"Avg Latency(usec): {result}")
        self.running_logger.info("-------------------------------------")


    def print_result(self, test_type, message_size, command, output, index, error_count):
        print(f"Server IP: {SERVER_IP}")
        print(f"Iter-Index: {index}")
        print(f"Error Count: {error_count}")
        print(f"Test Type: {test_type}")
        print(f"Message Size: {message_size}")
        print(f"Command: {' '.join(command)}")
        print(output)
        print("-------------------------------------")


    def log_total_avg(self, test_type, message_size, total_result, iteration, error_count, calculation_counts):
        self.running_logger.info(f" ======>>>>>> Total Average <<<<<<======")
        self.running_logger.info(f" Date: {dt.datetime.now()}")
        self.running_logger.info(f" Test Type: {test_type}")
        self.running_logger.info(f" Message Size: {message_size}")
        self.running_logger.info(f" Iteration: {iteration}")
        self.running_logger.info(f" Error Count: {error_count}")
        self.running_logger.info(f" Calculation Count: {calculation_counts}")
        if test_type == "throughput":
            self.running_logger.info(f" Bandwidth(Mbps): {total_result}")
        else:
            self.running_logger.info(f" Avg Latency(usec): {total_result}")
        self.running_logger.info("-------------------------------------")

        self.result_logger.info(f" ======>>>>>> Total Average <<<<<<======")
        self.result_logger.info(f" Date: {dt.datetime.now()}")
        self.result_logger.info(f" Test Type: {test_type}")
        self.result_logger.info(f" Message Size: {message_size}")
        self.result_logger.info(f" Iteration: {iteration}")
        self.result_logger.info(f" Error Count: {error_count}")
        self.result_logger.info(f" Calculation Count: {calculation_counts}")
        if test_type == "throughput":
            self.result_logger.info(f" Bandwidth(Mbps): {total_result}")
        else:
            self.result_logger.info(f" Avg Latency(usec): {total_result}")
        self.result_logger.info("-------------------------------------")


    def print_total_avg(self, test_type, message_size, total_result, iteration, error_count, calculation_counts):
        print(f" ======>>>>>> Total Average <<<<<<======")
        print(f" Date: {dt.datetime.now()}")
        print(f" Test Type: {test_type}")
        print(f" Message Size: {message_size}")
        print(f" Iteration: {iteration}")
        print(f" Error Count: {error_count}")
        print(f" Calculation Count: {calculation_counts}")
        if test_type == "throughput":
            print(f" Bandwidth(Mbps): {total_result}")
        else:
            print(f" Avg Latency(usec): {total_result}")
        print("-------------------------------------")
