module.exports = {
    SignIn: {
        InsertNumber: "Please enter your passcode.",
        SignIn: "Sign In",
        Authorizing: "Signing in...",
        Errors: {
            ServerNotResponding: "The server is not responding. Please try again later.",
            WrongCredential: "Please check if the user number is correct.",
            UnknownError: "Login failed. Please contact the researcher."
        },
        ConfirmSignOut: "Are you sure you want to sign out?",
        SignOut: "Sign Out",
        Cancel: "Cancel"
    },
    TopicSelection: {
        Title: "What shall we talk about today?",
        Plan: "What's the plan for today?",
        Recall: "What happened today?",
        FreeTemplate: "{child_name}'s favorite things",
        StarCount: "Check stars"
    },
    DyadInfo: {
        FamilyLabelTemplate: "{child_name} and {parent_type}",
        ParentType: {
            mother: "Mom",
            father: "Dad"
        }
    },
    Session: {
        StartingMessage: {
            PlanTemplate: "Start a conversation about what {child_name} will do today.",
            RecallTemplate: "Start a conversation about what {child_name} experienced today.",
            FreeTemplate: "Start a conversation on a topic {child_name} likes."
        },
        LoadingMessage: {
            Initializing: "Initializing...",
            ParentGuide: "Creating a conversation guide...",
            ChildCardsTemplate: "Selecting cards for {child_name}...",
            RefreshChildCards: "Preparing new cards...",
            ParentExample: "Creating example sentences...",
        },
        EndingMessage: "That was a great conversation!",
        Menu: {
            NextTurn: "Pass the conversation turn",
            TerminateSession: "End conversation",
            ConfirmTermination: "Are you sure you want to end the current conversation?",
            TerminateAndSave: "Save and end",
            TerminateWithoutSave: "End without saving",
            CancelTermination: "Cancel",
            GoHome: "Return to the home screen"
        },
        Cards: {
            Category: {
                topic: "Topic",
                action: "Action",
                emotion: "Emotion"
            }
        }
    }
}