from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import PromptTemplate
from utils import PrintStreamingSaveOutputCallback
from env import * # TODO: llm 종류, temperature 등 다양한 환경 변수 설정 추가 필요

from utils import AIScheduleParser

parser = AIScheduleParser()
parser("""[Chain of Thought (CoT) for Scheduling]
   First Step: Analysis of Request Task
   The request task involves classifying a question about where to smoke at Incheon International Airport into the most relevant department type from a provided list. The task requires logical reasoning to determine the appropriate department based on the context of the question. The question specifically asks for the location of smoking areas, which suggests that it relates to operational or customer service aspects of the airport. This indicates that the relevant department would likely be one that deals with customer experience or airport operations.

   Second Step: Reasoning scheduling strategy
   To accomplish this task, I will first need to analyze the question to identify the relevant department type. The sub-module "reference_module" can be used to process the inference task of determining the most suitable department based on the question about smoking areas. The input parameters for this sub-module will include the inference task (the question) and reference data (the list of department types). After determining the appropriate department, I will use the "answer_module" to format the output according to the specified answer format. The output from the reference_module will serve as the input for the answer_module.

   Last Step: Verification of Sub-Task Order
   The sequence of sub-tasks is logical: first, the question is analyzed to find the relevant department type, and then the result is formatted into the required output structure. There are no conflicting inputs, as the output of the first sub-task directly feeds into the second sub-task.

[Final Scheduling Result]
  - Sub-Task #1
    - Sub-Task Description: Analyze the question about smoking areas to determine the most relevant department type from the provided list.
    - Assigned Sub-Module: reference_module
    - Input Parameters & Values:
      - inference_task:
          - Input/Output Dependencies: None
          - Input Parameter Values: "인천공항 어디에서 흡연해야 하나요? 흡연실 위치를 알려주세요."
      - reference_data:
        - Input/Output Dependencies: None
        - Input Parameter Values: "경영본부 > ESG경영처 > ESG경영팀, 경영본부 > ESG경영처 > 경영지원팀, 경영본부 > ESG경영처 > 법무팀, 경영본부 > ESG경영처 > 윤리준법팀, 경영본부 > 인 재경영처 > 노사협력팀, 경영본부 > 인재경영처 > 복지후생팀, 경영본부 > 인재경영처 > 인사팀, 경영본부 > 자회사관리처 > 상생협력팀, 경영본부 > 자회사관리처 > 자회사경영팀, 경영본부 > 자회사관리처 > 자회사사업팀, 경영본부 > 재무처 > 계약팀, 경영본부 > 재무처 > 수입총괄팀, 경영본부 > 재무처 > 자산운영팀, 경영본부 > 재무처 > 재무팀, 경영본부 > 재무처 > 재산관리팀, 경영본 부 > 재무처 > 회계팀, 경영본부 > 항공교육원 > 교육기획팀, 경영본부 > 항공교육원 > 글로벌교육팀, 경영본부 > 항공교육원 > 인재양성팀, 경영본부 > 항공교육원 > 항공교육팀, 공항건설단 > 건 축처 > 건축계획팀, 공항건설단 > 건축처 > 건축공사1팀, 공항건설단 > 건축처 > 건축공사2팀, 공항건설단 > 공항계획처 > 공항계획팀, 공항건설단 > 공항계획처 > 단지조성팀, 공항건설단 > 공항계획처 > 토목공사팀, 공항건설단 > 기전통신처 > 기계설비팀, 공항건설단 > 기전통신처 > 전기설비팀, 공항건설단 > 기전통신처 > 통신시설팀, 공항건설단 > 토목처 > AS토목팀, 디지털혁신실 > DX기획팀, 비서실, 신사업본부 > 공항도시개발처 > 복합도시개발팀, 신사업본부 > 공항도시개발처 > 사업개발팀, 신사업본부 > 공항도시개발처 > 항공시설개발팀, 신사업본부 > 해외공항운영처 > 해외리스크관리팀, 신사업본부 > 해외공항운영처 > 해외사업운영팀, 신사업본부 > 해외사업개발처 > 해외사업개발1팀, 신사업본부 > 해외사업개발처 > 해외사업개발2팀, 신사업본부 > 해외사업개발처 > 해외사업전략팀, 신사업본부 > 허브화전략처 > 슬롯운영팀, 신사업본부 > 허브화전략처 > 항공마케팅팀, 신사업본부 > 허브화전략처 > 허브화기획팀, 운영본부 > 공항운영처 > 고객경험팀, 운영본부 > 공항운영처 > 문화예술공항팀, 운영본부 > 공항운영처 > 스마트서비스팀, 운영본부 > 공항운영처 > 운영기획팀, 운영본부 > 교통서비스처 > 교통계획팀, 운영본부 > 교통서비스처 > 교통시설팀, 운영본부 > 교통서비스처 > 교통운영팀, 운영본부 > 상업서비스처 > 면세사업팀, 운영본부 > 상업서비스처 > 상업서비스팀, 운영본부 > 상업서비스처 > 식음사업팀, 운영본부 > 항공물류처 > 물류개발팀, 운영본부 > 항공물류처 > 물류시설팀, 운영본부 > 항공물류처 > 물류운영팀, 운항본부 > 수하물운영처 > 수하물시설팀, 운항본부 > 수하물운영처 > 수하물운영1팀, 운항본부 > 수하물운영처 >  수하물운영2팀, 운항본부 > 운항관리처 > 계류장관제팀, 운항본부 > 운항관리처 > 계류장운영팀, 운항본부 > 운항관리처 > 운항계획팀, 운항본부 > 운항관리처 > 운항안전팀, 운항본부 > 운항시설처 > 비행장시설팀, 운항본부 > 운항시설처 > 소방시설팀, 운항본부 > 운항시설처 > 항공등화팀, 운항본부 > 항행처 > 계기착륙팀, 운항본부 > 항행처 > 공항레이더팀, 운항본부 > 항행처 > 미래항공 팀, 운항본부 > 항행처 > 지상레이더팀, 운항본부 > 항행처 > 항공통신팀, 인프라본부 > 공항시설처 > 건축지원팀, 인프라본부 > 공항시설처 > 시설계획팀, 인프라본부 > 공항시설처 > 조경팀, 인프라본부 > 공항시설처 > 토목시설팀, 인프라본부 > 스마트공항처 > 경영정보팀, 인프라본부 > 스마트공항처 > 공항정보팀, 인프라본부 > 스마트공항처 > 미디어통신팀, 인프라본부 > 스마트공항처 > 통신운영팀, 인프라본부 > 운송플랜트처 > 셔틀트레인팀, 인프라본부 > 운송플랜트처 > 승강시설팀, 인프라본부 > 운송플랜트처 > 자기부상열차팀, 인프라본부 > 운송플랜트처 > 플랜트시설팀, 인프라본부 > 친환경전력처 > 그린에너지팀, 인프라본부 > 친환경전력처 > 전력계통팀, 인프라본부 > 친환경전력처 > 전력운영팀, 인프라본부 > 친환경전력처 > 환경관리팀, 인프라본부 > 터미널시설처 > 시설환경팀, 인프라본부 > 터미널시설처 > 입주지원팀, 인프라본부 > 터미널시설처 > 터미널건축팀, 인프라본부 > 터미널시설처 > 터미널기계팀, 직할부서, 항공보안단 > 보안운영처 > 보안관리팀, 항공보안단 > 보안운영처 > 보안장비팀, 항공보안단 > 보안운영처 > 테러대응팀, 항공보안단 > 비상계획단, 항공보안단 > 사이버보안센터, 항공보안단 > 통합연대, 항공보안단 > 항공보안처 > 보 안검색팀, 항공보안단 > 항공보안처 > 보안계획팀"

  - Sub-Task #2
    - Sub-Task Description: Format the output to match the required answer format after determining the relevant department type.
    - Assigned Sub-Module: answer_module
    - Input Parameters & Values:
      - input_sentence:
          - Input/Output Dependencies: Sub-Task #1
          - Input Parameter Values: "처리부서:운영본부 > 공항운영처 > 고객경험팀"
      - answer_instructions:
        - Input/Output Dependencies: None
        - Input Parameter Values: "답변 형식: 처리부서:선택한 부서 유형""")

a = 1