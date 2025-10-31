
---

## 👨‍💻 프론트엔드 가이드

### 1부: 우리 프로젝트의 '지도' (폴더 구조)

"먼저, 코드를 찾기 쉽게 '관심사'에 따라 폴더를 나눴습니다. `src` 폴더가 핵심입니다."



* `src/assets`
    * "여기는 **이미지, CSS 파일**처럼 디자인에 필요한 '재료'들이 있습니다."
* `src/components` (⭐️ 중요)
    * "여기는 **'재사용 가능한 부품(레고 블럭)'**들이 모여있습니다. 버튼, 캘린더, 사이드바 같은 것들이죠."
    * `components/auth`: 로그인, 회원가입 폼처럼 '인증'에 관련된 부품들
    * `components/calendar`: '예약 모달'과 '캘린더' 부품
    * `components/graph`: 제일 중요한 **'네트워크 그래프'** 부품 (`NetworkGraph.vue`)
    * `components/profile`: 멘토 클릭 시 나오는 **'우측 사이드바'** 부품
* `src/views` (⭐️ 중요)
    * "여기는 `components`에서 만든 부품들을 **조립해서 만든 '완성된 페이지'**들입니다."
    * `NetworkView.vue`: 그래프, 사이드바, 모달을 모두 조립한 **핵심 메인 페이지**
    * `LoginView.vue`: 로그인 페이지
* `src/router`
    * "여기는 **'페이지 이동'**을 관리하는 GPS입니다."
    * `index.js`: "`/login`을 치면 `LoginView.vue`를 보여줘" 같은 규칙과, **"로그인 안 했으면 `/network` 못 가"** 같은 보안 규칙이 있습니다.
* `src/store` (⭐️⭐️ 아주 중요)
    * "여기는 우리 앱의 **'뇌(Brain)'** 또는 **'중앙 데이터 창고'**입니다."
    * "모든 페이지와 부품들이 공유하는 **공용 데이터**는 다 여기에 있습니다."
* `src/services`
    * "여기는 **백엔드와 통신하는 '직원'**입니다."
    * `api.js`: "백엔드 서버 주소는 `http://localhost:8000/api`야" 라고 설정해두는 파일입니다.

**(팀원 요약)**
"팀원분들이 찾고 싶은 기능이 있다면, **`views`(페이지)`**에서 시작해서, 그 페이지가 사용하는 **`components`(부품)`**를 찾아가고, 그 부품이 사용하는 **`store`(데이터)`**를 확인하시면 됩니다."

---

### 2부: 앱이 작동하는 '흐름' (핵심 로직)

"지금부터 사용자가 앱을 켰을 때부터 멘토를 예약하기까지, 코드가 어떻게 흘러가는지 순서대로 보여드릴게요."

**1. (가짜) 로그인 & 그래프 로드**

* "사용자가 `http://localhost:5173/network`로 접속을 시도합니다."
* `router/index.js` (GPS)가 "잠깐, 너 로그인했어?"라고 물어봅니다.
* `store/auth.js` (뇌)가 "응, **`MOCK_LOGIN`** 변수가 `true`라서 '가짜 로그인' 상태야"라고 답합니다. (백엔드가 없어도 개발하기 위해 설정했습니다.)
* 라우터가 통과시키면, `views/NetworkView.vue` 페이지가 열립니다.
* `NetworkView`가 "그래프 데이터 줘"라고 `store/network.js` (뇌)에 요청합니다.
* `network.js`가 "응, **`MOCK_DATA`** 변수가 `true`라서 '가짜 그래프 데이터' 줄게"라고 답합니다. (이것도 테스트용입니다.)
* `NetworkView`가 이 데이터를 `components/graph/NetworkGraph.vue` 부품에 넘겨줘서 화면에 그래프가 그려집니다.

**2. 멘토 클릭 & 사이드바 (⭐️ 핵심 변수)**

* "사용자가 그래프에서 '한법무' 멘토 노드를 클릭합니다."
* `NetworkView.vue`에 있는 **`handleNodeClick`** (노드클릭처리) 함수가 실행됩니다.
* 이 함수는 **`selectedMentor`** 라는 변수(상태)에 '한법무' 멘토의 정보를 저장합니다. (원래 이 변수는 `null`이었습니다.)
* `components/profile/MentorSidebar.vue` (사이드바)는 이 **`selectedMentor`** 변수를 계속 감시하고 있다가,
* "어? 변수에 `null`이 아니라 멘토 정보가 들어왔네?" 하면서 화면 우측에 '짠'하고 나타납니다.
* *(반대로, 사용자가 'CPA' 같은 멘토 아닌 노드를 클릭하면 `selectedMentor` 변수는 다시 `null`이 되고, 사이드바는 사라집니다.)*

**3. 예약하기 & 모달**

* "사용자가 사이드바에서 '커피챗 예약하기' 버튼을 누릅니다."
* `NetworkView.vue`에 있는 **`openBookingModal`** (예약모달열기) 함수가 실행됩니다.
* 이 함수는 **`isModalOpen`** 이라는 변수(상태)를 `false`에서 `true`로 바꿉니다.
* `components/calendar/BookingModal.vue` (예약 모달)은 이 **`isModalOpen`** 변수를 감시하고 있다가,
* "어? `true`로 바뀌었네?" 하면서 화면 중앙에 '짠'하고 나타납니다.

**(팀원 요약)**
"모든 상호작용은 `NetworkView.vue`가 '지휘자'처럼 통제합니다. **`selectedMentor`**라는 변수가 **사이드바의 열림/닫힘**을, **`isModalOpen`**이라는 변수가 **모달의 열림/닫힘**을 결정합니다."

---

### 3부: 백엔드 없이 테스트하는 법 (가짜 스위치)

"지금 백엔드가 없어도 프론트가 완벽하게 돌아가는 이유는, `store` 폴더에 '가짜 스위치'를 만들어뒀기 때문입니다."

* `src/store/auth.js` (인증)
    * 파일 맨 위에 `const MOCK_LOGIN = true;` 가 있습니다.
    * `true`면: **강제 로그인** (그래서 `/network`에 바로 접속됩니다.)
    * `false`면: **실제 로그인** (그래서 `/login` 페이지만 보입니다.)

* `src/store/network.js` (데이터)
    * 파일 맨 위에 `const MOCK_DATA = true;` 가 있습니다.
    * `true`면: **가짜 그래프 데이터**를 사용합니다. (제가 1단계에서 만든 것)
    * `false`면: **실제 백엔드 API** (`/api/network/{userId}`)를 호출합니다.

---
회원가입 로그인 관련된 아이들은 src components auth에 있어용
network창 보려면 store auth.js network.js true로 바꾸면 됩니다
  
