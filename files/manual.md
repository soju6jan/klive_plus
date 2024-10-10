### 팬더TV
  - sesskey 값이 없는 경우 19금 방송 제외
  - F12 개발자 모드 - 로그인 후   
    네트워크탭 - 아무요청 - Headers Cookie   
    sessKey= 이후 ; 까지 값   
    <img src="https://i.imgur.com/6KiVzzd.png" width="70%" height="70%" />

<hr style="height: 3px; background-color: black; border: none;">

### 팝콘TV
  - 4가지 값 필수. SNS 로그인 지원 안함.   
    ID / PW   
  - F12 개발자 모드 - 로그인
    login URL 선택 - Basic으로 시작하는 Authorization 값   
    <img src="https://i.imgur.com/91RCbdS.png" width="70%" height="70%" />

  - 방송재생 
    castwatchonoff URL 선택 - Headers
    ClientKey 값.   
    <img src="https://i.imgur.com/3130QQU.png" width="70%" height="70%" />
