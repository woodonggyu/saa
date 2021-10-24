# AWS WAF (Web Application Firewall) 구축 및 활용

AWS WAF (Web Application Firewall) 은 AWS 환경에서 발생하는 Layer 7 에 해당하는 보안 위협 (DDoS 공격 또는 웹 애플리케이션 공격) 에 대응하기 위한 보안 서비스이다. 배포할 수 있는 리소스는 다음과 같다.
* CloudFront
* Application LoadBalancer
* API Gateway 또는 AWS AppSync

<br>

AWS WAF 서비스를 구축하기 전, 3rd Party 제품과 비교해 어떤 차이점이 있는지 간략히 설명한다. 

1. **Infrastructure**
보안 인프라 운영을 담당하는 입장에서는 어떠한 솔루션을 구축할 때, 장애 발생에 대한 대응 방안을 고려하는 것은 필수적이라고 할 수 있다. 이러한 관점에서 3rd Party 제품을 AWS 환경에 인라인으로 단일 또는 이중화 구성을 한다고 가정해보자. 
간략하게 설명하면 (FNAT로 인해) 통신 구조가 복잡해지고, 증가하는 트래픽에 대한 Scalable 구성이 어려워 장애 포인트가 될 수 있다. 또한, 장애 발생에 대한 Bypass 방안 또는 (A-S) 구성에서 EIP 또는 ENI 를 Standby 인스턴스로 매핑해야 하는 등 여러 상황에 대한 대응 프로세스를 수립해야 한다. 

2. **Threat Detection**
위협 탐지 관점에서 AWS WAF 서비스가 출시되었을 때, 탐지 성능이 좋지 않았다고 한다. 하지만, AWS Marketplace 를 통해 보안 벤더사의 Ruleset 을 구매하여 사용할 수 있다.

요약해서 말하자면, AWS WAF 서비스는 인프라 운영 관점에서 안정적이고 가용성 높은 서비스이고, 아쉬운 부분에 대해서 빠르게 기능을 개선하고 있어 굳이 3rd Party 제품을 도입할 이유가 없어지고 있다.

<br>

## AWS WAF 활용한 웹 애플리케이션 공격 탐지

구성 목표는 두 개의 가용영역에 웹 서비스를 구축하고, ALB (Application LoadBalancer) 로 연결한다. 그리고 애플리케이션 로드밸런서에 `AWS WAF (Web Application Firewall)` 서비스를 배포하여 웹 서비스에 대한 공격을 탐지한다. 구성은 아래와 같다.

![](https://images.velog.io/images/woodonggyu/post/999775f8-c467-45aa-8cc2-6eb7ff982ae7/image.png)

<br>

### 1. WebACL 생성

"Create WebACL" 을 선택하면 나오는 기본 화면이다. `WebACL 을 생성할 리전` 과 함께 `리소스 타입 (CloudFront 또는 Regional Resource)` 를 선택해야 한다.

![](https://images.velog.io/images/woodonggyu/post/45d9d165-377a-421f-91e9-6e6583b3f67b/image.png)

<br>

연결할 AWS 리소스를 지정할 수 있다. 당장 연결할 필요는 없으며, 향후에라도 지정하고자 하는 리소스를 선택하면 된다.

![](https://images.velog.io/images/woodonggyu/post/a9ed7ce3-78a4-423a-97a3-94040b1d0647/image.png)

<br>

가장 중요한 부분이다. 탐지 룰셋을 정의할 수 있으며, 사용자 요청이 룰셋에 매칭되지 않을 경우에 대한 기본 액션 (허용/차단 여부) 을 설정할 수 있다. 룰셋은 AWS 관리 및 제공해주는 룰을 사용하거나 사용자가 원하는 형태로 룰을 작성할 수 있다.

* [Managed rule groups](https://docs.aws.amazon.com/waf/latest/developerguide/waf-managed-rule-groups.html)
* [Managing your own rule groups](https://docs.aws.amazon.com/waf/latest/developerguide/waf-user-created-rule-groups.html)

![](https://images.velog.io/images/woodonggyu/post/400f5c7c-a6d4-48d6-a2ee-7152810c405d/image.png)

<br>

룰셋을 설정했다면, 매칭 우선순위를 설정할 수 있다.
(첫 번째 룰셋에서 매칭되었을 경우, 다음 룰셋에 매칭 여부를 확인하는지 등 상세 로직은 확인 필요)

![](https://images.velog.io/images/woodonggyu/post/ec77b5d2-e818-4408-877f-62efe8591501/image.png)

<br>

마지막으로 CloudWatch 메트릭 설정이다. 모니터링 허용 여부를 결정할 수 있다.

![](https://images.velog.io/images/woodonggyu/post/3d7dfee8-b7d5-4776-8eb6-c65a5d839539/image.png)

<br>

### 2. 룰셋 생성 예시

기본적으로 AWS WAFv2 에서는 JSON 포맷을 활용한 룰 생성이 가능하다.

#### 2-1. 국가 기반의 IP 차단

출발지 국가가 중국일 경우, 차단한다.

```JSON
{
  "Name": "COUNTRY_BLOCK_CHINA",
  "Priority": 0,
  "Action": {
    "Block": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "COUNTRY_BLOCK_CHINA"
  },
  "Statement": {
    "GeoMatchStatement": {
      "CountryCodes": [
        "CN"
      ]
    }
  }
}
```

#### 2-2. 속도 기반의 IP 차단

특정 출발지 주소에서 5분 동안 1,000번 이상 웹 요청 시, 차단한다.

```
{
  "Name": "MAX_REQUEST_1000",
  "Priority": 0,
  "Action": {
    "Block": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "MAX_REQUEST_1000"
  },
  "Statement": {
    "RateBasedStatement": {
      "Limit": "1000",
      "AggregateKeyType": "IP"
    }
  }
}
```

#### 2-3. HTTP Header 기반의 요청 차단

매칭을 시도할 헤더는 "User-Agent" 이고, 해당 헤더 내 대소문자 구분없이 "python" 문자열이 포함되어 있을 경우, 차단한다.

```
{
  "Name": "USERAGENT_BLOCK_PYTHON",
  "Priority": 0,
  "Action": {
    "Block": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "USERAGENT_BLOCK_PYTHON"
  },
  "Statement": {
    "ByteMatchStatement": {
      "FieldToMatch": {
        "SingleHeader": {
          "Name": "User-Agent"
        }
      },
      "PositionalConstraint": "CONTAINS",
      "SearchString": "python",
      "TextTransformations": [
        {
          "Type": "LOWERCASE",
          "Priority": 0
        }
      ]
    }
  }
}
```

<br>

### 3. 리소스 관리 및 운영 자동화

우리는 보통 AWS Management Console 에서 인프라와 더불어 관련 리소스들을 수동으로 생성한다. 소규모의 인프라는 조금 번거롭더라도 어렵지 않게 운영할 수 있을지 모르겠지만, 대규모 클라우드 인프라 구축에서는 많은 실수가 발생하고 이는 곧 보안 이슈로 직결될 수 있다.

위와 같은 문제를 해결하기 위해 AWS 에서 제공하는 CloudFormation 및 Terraform 과 같은 클라우드 인프라 자동화 도구를 활용해 손쉽게 클라우드 인프라를 구축 및 관리할 수 있다.

아래의 링크는 **`terraform`** 을 활용한 WebACL 생성 코드를 제공한다. 룰 타입 별 예제 코드를 제공하고 있으며, 현재 논리 연산자를 활용한 룰 생성을 지원하지 않는다. (2021.10.24 기준)
* https://github.com/woodonggyu/terraform-aws-wafv2
 
<br>

AWS 에서는 모든 리소스가 API 를 통해 제어가 가능하며, SDK(Software Development Kit) 를 제공한다.
따라서, 우리는 AWS SDK 를 활용하여 생성한 리소스에 대해 운영을 자동화할 수 있다.

마찬가지로 아래의 링크를 통해 IP set 을 활용한 차단 IP 등록을 위한 코드를 제공한다.
* https://github.com/woodonggyu/sac/tree/main/aws/wafv2