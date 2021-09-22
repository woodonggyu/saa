# AWS Management Console 접근 제어 (based on Source IP)

AWS Management Console은 Amazon 서비스 액세스 및 관리를 위한 웹 기반 인터페이스이다.

브라우저를 기반으로 리소스를 시각적이고 이해하기 쉬운 형태로 관리할 수 있도록 지원한다.

<br>

일반적으로 AWS Management Console 에서는 별도의 IAM 정책이 없다면, 어느 곳에서나 (리소스)접근이 가능하기에 Public Cloud 사용하는 조직의 입장에서는 보안 이슈로 여겨진다.

<br>

AWS(Amazone Web Service)는 공인망이기에 어디에서나 접근 가능하다. 따라서 AWS Management Console에 대한 직접적인 접근 제어는 불가능하다.

그렇기에 정확하게는 Console 접근을 막는게 아닌 **IAM 정책을 통해 특정 IP 주소를 제외하고서는 AWS 리소스를 사용하는 것을 제한한다.**

IAM 정책을 통해 접근 제어 관리 및 리소스에 대한 최소한의 권한을 부여하고 운영함으로써, 혹시나 발생할 수 있는 침해사고(ex. 계정 유출)에 대한 2차 피해를 최소화할 수 있다.

<br>

특정 IP 주소를 제외한 모든 리소스에 대한 접근을 Deny 하는 정책은 다음과 같다.
```json
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Deny",
        "Action": "*",
        "Resource": "*",
        "Condition": {
            "NotIpAddress": {
                "aws:SourceIp": ""
            }
        }
    }
}
```

<br>

> ##### 일부 서비스의 경우, 접근 가능한 IP 주소임에도 불구하고 접근이 불가능할 수 있다. 관련 이슈 발생 시, NotAction 요소에 접근하고자 하는 서비스를 추가한다.
