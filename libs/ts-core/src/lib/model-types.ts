interface ModelWithIdAndTimestamp{
    id: string
    timestamp: number
}

export interface CardIdentity{
    id: string
    recommendation_id: string
}

export enum CardCategory{
    Topic="topic",
    Emotion="emotion",
    Action="action",
    Core="core"
}

export interface CardInfo extends CardIdentity{
    label: string
    label_localized: string
    category: CardCategory
}

export interface CardImageMatching{
    id: string
    card_info_id: string
    type: "stock" | "custom"
    image_id: string
}

export interface ChildCardRecommendationResult extends ModelWithIdAndTimestamp{
    cards: Array<CardInfo>
}

export enum ParentGuideType {
    Messaging = "messaging",
    Feedback = "feedback"
}

export enum DialogueInspectionCategory{
    Blame = "blame",
    Correction = "correction",
    Complex = "complex",
    Deviation = "deviation"
}

export enum ParentGuideCategory{
    Intention="intention",
    Specification="specification",
    Choice="choice",
    Clues="clues",
    Coping="coping",
    Stimulate="stimulate",
    Share="share",
    Empathize="empathize",
    Encourage="encourage",
    Emotion="emotion",
    Extend="extend",
    Terminate="terminate"
}

export interface ParentGuideElement{
    id: string
    category: ParentGuideCategory | ReadonlyArray<DialogueInspectionCategory>,
    guide: string
    guide_localized?: string | undefined | null
    type: ParentGuideType
}

export interface ParentGuideRecommendationResult extends ModelWithIdAndTimestamp{
    guides: Array<ParentGuideElement>
}

export interface ParentExampleMessage extends ModelWithIdAndTimestamp{
    recommendation_id?: string
    guide_id?: string
    message: string
    message_localized?: string
}

export enum DialogueRole{
    Parent="parent",
    Child="child"
}

export interface DialogueMessage{
    role: DialogueRole
    content_localized?: string
    content: string | Array<CardInfo>
    recommendation_id?: string
}

type Dialogue = Array<DialogueMessage>

export enum ParentType{
    Mother="mother",
    Father="father"
}

export interface Dyad{
  id: string
  alias: string
  child_name: string
  parent_type: ParentType
}

export interface DyadWithPasscode extends Dyad{
    passcode: number
}

export enum TopicCategory{
    Plan="plan",
    Recall="recall",
    Free="free"
}

export const TOPIC_CATEGORIES = [TopicCategory.Plan, TopicCategory.Recall, TopicCategory.Free]

export interface SessionTopicInfo{
    category: TopicCategory
    subtopic?: string
    subdescription?: string 
}

export interface FreeTopicDetail{
    id: string
    subtopic: string
    subtopic_description: string
}

export interface TurnIdWithPayload<T>{
    payload: T
    next_turn_id: string
}

export enum SessionStatus {
    Initial="initial",
    Started="started",
    Conversation="conversation",
    Terminated="terminated"
}

export interface ExtendedSessionInfo{
    id: string

    dyad_id: string
    topic: SessionTopicInfo
    status: SessionStatus
    local_timezone: string
    started_timestamp: number

    ended_timestamp: number
    
    num_turns: number
}