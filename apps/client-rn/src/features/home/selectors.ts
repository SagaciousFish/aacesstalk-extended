import { createSelector } from "@reduxjs/toolkit";
import { sessionInfoEntitySelectors } from "libs/ts-core/src/lib/redux/reducers/dyad-status";
import moment from 'moment-timezone'
import groupArray from 'group-array'
import { ExtendedSessionInfo } from "@aacesstalk/libs/ts-core";

export const dailyStarStatsSelector = createSelector([
    sessionInfoEntitySelectors.selectAll
], (sessions) => {
    const sessionsWithDate = sessions.map(s => ({session: s, date_ts: moment.tz(s.started_timestamp, s.local_timezone).startOf('day').format('YYYY-MM-DD')}))
    const groupedByDay: {[key:string]: Array<{session: ExtendedSessionInfo, date_ts: string}>} = groupArray(sessionsWithDate, 'date_ts') as any

    const summaryList: Array<{dateString: string, numDialogues: number, numStarsTotal: number}> = []
    for(const dateString of Object.keys(groupedByDay)){
        const sessions = groupedByDay[dateString].map(sd => sd.session)

        const numDialogues = sessions.length
        const numStarsTotal = sessions.reduce((partialSum, curr) => {
            return partialSum + Math.floor(curr.num_turns/2)
        }, 0)

        summaryList.push({
            dateString,
            numDialogues,
            numStarsTotal
        })
    }

    summaryList.sort((a, b) => {
        return moment(b.dateString, "YYYY-MM-DD").unix() - moment(a.dateString, "YYYY-MM-DD").unix()
    })

    return {
        summaryList, 
        totalStars: summaryList.reduce((sum, s) => sum + s.numStarsTotal, 0)
    }
})