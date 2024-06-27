module.exports = {
    SignIn: {
        InsertNumber: "사용자 번호를 입력해주세요.",
        SignIn: "로그인",
        Authorizing: "로그인 중입니다...",
        Errors: {
            ServerNotResponding: "서버가 응답하지 않습니다. 잠시 후에 다시 시도해 주세요.",
            WrongCredential: "사용자 번호가 올바른지 확인해 주세요.", 
            UnknownError: "로그인이 실패하였습니다. 연구자에게 문의해 주세요."
        },
        ConfirmSignOut: "로그아웃 하시겠습니까?",
        SignOut: "로그아웃",
        Cancel: "취소"
    },
    TopicSelection: {
        Title: "오늘은 어떤 이야기를 할까요?",
        Plan: "오늘 뭐하지?",
        Recall: "오늘 무슨 일이 있었지?",
        FreeTemplate: "{child_name}가 좋아하는 것",
        StarCount: "별 확인하기"
    },
    DyadInfo: {
        FamilyLabelTemplate: "{child_name}와 {parent_type}",
        ParentType: {
            mother: "엄마",
            father: "아빠"
        }
    },
    Session: {
        StartingMessage: {
            PlanTemplate: "{child_name}가 오늘 할 일에 대해 대화를 시작해 보세요.",
            RecallTemplate: "{child_name}가 오늘 겪었던 일에 대해 대화를 시작해 보세요.",
            FreeTemplate: "{child_name}가 좋아하는 주제로 대화를 시작해 보세요."
        },
        LoadingMessage: {
            Initializing: "준비중입니다...",
            ParentGuide: "대화 가이드를 만드는 중입니다...",
            ChildCardsTemplate: "{child_name}를 위한 카드를 고르고 있습니다...",
            RefreshChildCards: "새로운 카드들을 준비중입니다...",
            ParentExample: "예시 문장을 만드는 중입니다...",
        },
        EndingMessage: "멋진 대화였어요!",
        Menu: {
            NextTurn: "대화 턴 넘기기",
            TerminateSession: "대화 종료하기",
            ConfirmTermination: "현재 대화를 종료하시겠습니까?",
            TerminateAndSave: "저장하고 종료하기",
            TerminateWithoutSave: "저장하지 않고 종료하기",
            CancelTermination: "취소",
            GoHome: "처음 화면으로 돌아가기"
        },
        Cards: {
            Category:{
                topic: "주제",
                action: "행동",
                emotion: "감정"
            }
        }
    }
}