package ru.poryadok5.app

import ru.poryadok5.app.domain.CountdownTimerRules
import org.junit.Assert.assertEquals
import org.junit.Test

class CountdownTimerRulesTest {
    @Test
    fun endTimeUsesRemainingSeconds() {
        val endAt = CountdownTimerRules.endAtMillis(nowMillis = 10_000L, remainingSeconds = 300)

        assertEquals(310_000L, endAt)
    }

    @Test
    fun remainingSecondsRoundsUpPartialSecond() {
        val remaining = CountdownTimerRules.remainingSeconds(endAtMillis = 12_001L, nowMillis = 10_500L)

        assertEquals(2, remaining)
    }

    @Test
    fun remainingSecondsCatchesUpAfterLongBackgroundGap() {
        val endAt = CountdownTimerRules.endAtMillis(nowMillis = 10_000L, remainingSeconds = 180)

        val remaining = CountdownTimerRules.remainingSeconds(endAtMillis = endAt, nowMillis = 190_000L)

        assertEquals(0, remaining)
    }

    @Test
    fun negativeRemainingInputCreatesExpiredTimer() {
        val endAt = CountdownTimerRules.endAtMillis(nowMillis = 10_000L, remainingSeconds = -5)

        assertEquals(10_000L, endAt)
    }
}
