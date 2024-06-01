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
            ParentGuide: "대화 가이드를 만드는 중입니다..."
        }
    }
}