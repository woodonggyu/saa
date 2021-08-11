# 계정 MFA(Multi-Factor Authentication) 강제화

**다단계 인증(MFA, Multi-Factor Authentication)**이란, 계정 인증 프로세스에 최소한 2번 이상의 인증 요소를 추가하는 것을 뜻한다. 

대표적으로는 생체 인증, 모바일 장치를 통한 인증 등이 있다. 

가장 많이 쓰이는 ID-PW 인증 방식의 경우, 간단하지만 여러 가지 단점이 존재한다.
- 신원 확인 불가능 (계정 유출 시, 누구나 접속이 가능하다.)
- 동일한 계정 정보 사용에 따른 2차 피해 발생 가능성
- 무차별(Brute-Force) 공격에 취약

즉, 기존의 ID-PW 인증 방식으로는 계정을 안전하게 관리하기 어렵다.

<br>

특히나 기업의 입장에서는 계정이 유출될 경우, 강력한 네트워크 경계에 대한 보안을 무력화하여 손쉽게 내부망으로 접근할 수 있기에 철저한 관리가 요구된다.

<br>

AWS 에서도 다단계 인증을 위한 여러 방법이 존재한다.

대표적으로는 Virtual MFA Device, Hardware MFA Device, SMS 문자 메시지 MFA 등이 있다.

* [AWS에서 Multi-Factor Authentication(MFA) 사용](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_mfa.html)

<br>

우리는 IAM 정책을 통해 MFA(Multi-Factor Authentication)이 적용되지 않은 유저에게는 AWS Console 내에서 어떠한 작업도 할 수 없도록 할 수 있다.
* [AWS: MFA 인증 IAM 사용자가 [내 보안 자격 증명(My Security Credentials)] 페이지에서 자신의 자격 증명을 관리할 수 있도록 허용](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/reference_policies_examples_aws_my-sec-creds-self-manage.html)

<br>

AWS 에서 제공하는 문서를 참고할 경우, 몇 가지 문제가 발생한다.

1. **패스워드 변경 권한 없음**  
AM 계정 생성 시, "Require password reset" 옵션을 활성화하는 경우 MFA 설정 전에 패스워드 변경에 대한 권한이 없어 로그인이 불가능하다.

2. **Virtual MFA Device 삭제 불가**  
MFA 인증 등록 과정에서 문제가 발생하는 경우 (ex. 세션이동, OTP 인증 실패 등), 생성된 임시 MFA 삭제가 불가능하다.

<br>

위와 같은 문제를 해결하기 위해서 다음과 같이 권한을 추가할 수 있다.

NotAction 요소에 "iam:ChangePassword", "iam:DeleteVirtualMFADevice", "iam:GetAccountPasswordPolicy" 권한을 추가하였다.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowGetAccountPasswordPolicy",
      "Effect": "Allow",
      "Action": [
        "iam:GetAccountPasswordPolicy"
      ],
      "Resource": "*"
    }, {
      "Sid": "AllowViewAccountInfo",
      "Effect": "Allow",
      "Action": [
        "iam:GetAccountPasswordPolicy",
        "iam:GetAccountSummary",
        "iam:ListVirtualMFADevices"
      ],
      "Resource": "*"
    }, {
      "Sid": "AllowManageOwnPasswords",
      "Effect": "Allow",
      "Action": [
        "iam:ChangePassword",
        "iam:GetUser"
      ],
      "Resource": "arn:aws:iam::*:user/${aws:username}"
    }, {
      "Sid": "AllowManageOwnAccessKeys",
      "Effect": "Allow",
      "Action": [
        "iam:CreateAccessKey",
        "iam:DeleteAccessKey",
        "iam:ListAccessKeys",
        "iam:UpdateAccessKey"
      ],
      "Resource": "arn:aws:iam::*:user/${aws:username}"
    }, {
      "Sid": "AllowManageOwnSigningCertificates",
      "Effect": "Allow",
      "Action": [
        "iam:DeleteSigningCertificate",
        "iam:ListSigningCertificates",
        "iam:UpdateSigningCertificate",
        "iam:UploadSigningCertificate"
      ],
      "Resource": "arn:aws:iam::*:user/${aws:username}"
    }, {
      "Sid": "AllowManageOwnSSHPublicKeys",
      "Effect": "Allow",
      "Action": [
        "iam:DeleteSSHPublicKey",
        "iam:GetSSHPublicKey",
        "iam:ListSSHPublicKeys",
        "iam:UpdateSSHPublicKey",
        "iam:UploadSSHPublicKey"
      ],
      "Resource": "arn:aws:iam::*:user/${aws:username}"
    }, {
      "Sid": "AllowManageOwnGitCredentials",
      "Effect": "Allow",
      "Action": [
        "iam:CreateServiceSpecificCredential",
        "iam:DeleteServiceSpecificCredential",
        "iam:ListServiceSpecificCredentials",
        "iam:ResetServiceSpecificCredential",
        "iam:UpdateServiceSpecificCredential"
      ],
      "Resource": "arn:aws:iam::*:user/${aws:username}"
    }, {
      "Sid": "AllowManageOwnVirtualMFADevice",
      "Effect": "Allow",
      "Action": [
        "iam:CreateVirtualMFADevice",
        "iam:DeleteVirtualMFADevice"
      ],
      "Resource": "arn:aws:iam::*:mfa/${aws:username}"
    }, {
      "Sid": "AllowManageOwnUserMFA",
      "Effect": "Allow",
      "Action": [
        "iam:DeactivateMFADevice",
        "iam:EnableMFADevice",
        "iam:ListMFADevices",
        "iam:ResyncMFADevice"
      ],
      "Resource": "arn:aws:iam::*:user/${aws:username}"
    }, {
      "Sid": "DenyAllExceptListedIfNoMFA",
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "iam:GetUser",
        "iam:ListMFADevices",
        "iam:ListVirtualMFADevices",
        "iam:ResyncMFADevice",
        "iam:DeleteVirtualMFADevice",
        "iam:ChangePassword",
        "iam:GetAccountPasswordPolicy",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```