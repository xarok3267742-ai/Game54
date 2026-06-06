package ru.poryadok5.app.domain

import java.time.LocalDate

internal fun normalizedCompletedTaskIds(ids: Set<String>): Set<String> {
    return ids.mapNotNullTo(mutableSetOf()) { rawId ->
        rawId.trim().takeIf(String::isNotEmpty)
    }
}

internal fun normalizedLastDoneDate(rawDate: String?): String? {
    return rawDate
        ?.trim()
        ?.takeIf(String::isNotEmpty)
        ?.let { candidate ->
            runCatching { LocalDate.parse(candidate) }.getOrNull()?.toString()
        }
}

fun UserProgress.withCompletedTask(taskId: String, today: LocalDate = LocalDate.now()): UserProgress {
    val normalizedTaskId = taskId.trim()
    val normalizedTotalDone = totalDone.coerceAtLeast(0)
    val normalizedStreakDays = streakDays.coerceAtLeast(0)
    val normalizedCompletedTaskIds = normalizedCompletedTaskIds(completedTaskIds)
    val safeLastDoneDate = normalizedLastDoneDate(lastDoneDate)
    if (normalizedTaskId.isEmpty()) {
        return copy(
            totalDone = normalizedTotalDone,
            streakDays = normalizedStreakDays,
            lastDoneDate = safeLastDoneDate,
            completedTaskIds = normalizedCompletedTaskIds,
        )
    }
    val previousDate = safeLastDoneDate?.let(LocalDate::parse)
    val nextStreak = when {
        previousDate == null -> 1
        previousDate == today -> normalizedStreakDays.coerceAtLeast(1)
        previousDate.plusDays(1) == today -> normalizedStreakDays + 1
        else -> 1
    }
    return copy(
        totalDone = normalizedTotalDone + 1,
        streakDays = nextStreak,
        lastDoneDate = today.toString(),
        completedTaskIds = normalizedCompletedTaskIds + normalizedTaskId,
    )
}
