package ru.poryadok5.app.domain

object CountdownTimerRules {
    fun endAtMillis(nowMillis: Long, remainingSeconds: Int): Long {
        return nowMillis + remainingSeconds.coerceAtLeast(0) * 1_000L
    }

    fun remainingSeconds(endAtMillis: Long, nowMillis: Long): Int {
        val millisLeft = endAtMillis - nowMillis
        if (millisLeft <= 0L) return 0
        return ((millisLeft + 999L) / 1_000L).coerceAtMost(Int.MAX_VALUE.toLong()).toInt()
    }
}
