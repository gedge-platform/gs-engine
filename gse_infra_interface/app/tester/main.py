from sockperfTester import SockperfTester
from settings import ITERATION

if __name__ == "__main__":
    # 결과를 저장할 파일 경로
    running_log_file = "running.txt"
    result_log_file = "result.txt"


    iteration = ITERATION

    # SockperfTester 인스턴스 생성 및 테스트 실행
    tester = SockperfTester(running_log_file, result_log_file)
    tester.run_tests(iteration)

    # 결과 파일 경로 출력
    print("Results saved to: {0}, {1}".format(running_log_file, result_log_file))