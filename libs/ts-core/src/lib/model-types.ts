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
    Action="action"
}

export interface CardInfo extends CardIdentity{
    label: string
    label_localized: string
    category: CardCategory
}

export interface ChildCardRecommendationResult extends ModelWithIdAndTimestamp{
    cards: ReadonlyArray<CardCategory>
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
    guides: ReadonlyArray<ParentGuideElement>
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
