package ru.poryadok5.app

import ru.poryadok5.app.domain.UserProgress
import ru.poryadok5.app.domain.withCompletedTask
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDate

class ProgressRulesTest {
    @Test
    fun firstCompletionStartsStreak() {
        val today = LocalDate.of(2026, 5, 27)

        val progress = UserProgress().withCompletedTask("home_001", today)

        assertEquals(1, progress.totalDone)
        assertEquals(1, progress.streakDays)
        assertEquals("2026-05-27", progress.lastDoneDate)
        assertTrue("home_001" in progress.completedTaskIds)
    }

    @Test
    fun sameDayCompletionDoesNotIncreaseStreakTwice() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(
            totalDone = 7,
            streakDays = 3,
            lastDoneDate = "2026-05-27",
            completedTaskIds = setOf("home_001"),
        )

        val next = progress.withCompletedTask("home_002", today)

        assertEquals(8, next.totalDone)
        assertEquals(3, next.streakDays)
        assertEquals(setOf("home_001", "home_002"), next.completedTaskIds)
    }

    @Test
    fun nextDayCompletionContinuesStreak() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(streakDays = 3, lastDoneDate = "2026-05-26")

        val next = progress.withCompletedTask("home_003", today)

        assertEquals(4, next.streakDays)
    }

    @Test
    fun missedDayResetsStreak() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(streakDays = 8, lastDoneDate = "2026-05-20")

        val next = progress.withCompletedTask("home_004", today)

        assertEquals(1, next.streakDays)
    }

    @Test
    fun malformedStoredDateResetsStreakWithoutCrashing() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(
            totalDone = 4,
            streakDays = 6,
            lastDoneDate = "bad-date",
            completedTaskIds = setOf("home_001"),
        )

        val next = progress.withCompletedTask("home_005", today)

        assertEquals(5, next.totalDone)
        assertEquals(1, next.streakDays)
        assertEquals("2026-05-27", next.lastDoneDate)
        assertEquals(setOf("home_001", "home_005"), next.completedTaskIds)
    }

    @Test
    fun blankCompletionClearsMalformedStoredDate() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(
            totalDone = 4,
            streakDays = 2,
            lastDoneDate = "bad-date",
            completedTaskIds = setOf(" home_001 "),
        )

        val next = progress.withCompletedTask("   ", today)

        assertEquals(4, next.totalDone)
        assertEquals(2, next.streakDays)
        assertEquals(null, next.lastDoneDate)
        assertEquals(setOf("home_001"), next.completedTaskIds)
    }

    @Test
    fun corruptedNegativeCountersAreNormalizedOnCompletion() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(
            totalDone = -10,
            streakDays = -3,
            lastDoneDate = "2026-05-26",
            completedTaskIds = setOf("", " home_001 ", " "),
        )

        val next = progress.withCompletedTask("home_006", today)

        assertEquals(1, next.totalDone)
        assertEquals(1, next.streakDays)
        assertEquals(setOf("home_001", "home_006"), next.completedTaskIds)
    }

    @Test
    fun blankCompletionDoesNotIncrementProgress() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(
            totalDone = -2,
            streakDays = -1,
            lastDoneDate = "2026-05-26",
            completedTaskIds = setOf("home_001", ""),
        )

        val next = progress.withCompletedTask("   ", today)

        assertEquals(0, next.totalDone)
        assertEquals(0, next.streakDays)
        assertEquals("2026-05-26", next.lastDoneDate)
        assertEquals(setOf("home_001"), next.completedTaskIds)
    }

    @Test
    fun completionTaskIdIsTrimmedBeforeStorage() {
        val today = LocalDate.of(2026, 5, 27)

        val next = UserProgress().withCompletedTask(" home_007 ", today)

        assertEquals(setOf("home_007"), next.completedTaskIds)
    }

    @Test
    fun existingCompletedTaskIdsAreTrimmedOnCompletion() {
        val today = LocalDate.of(2026, 5, 27)
        val progress = UserProgress(
            totalDone = 2,
            streakDays = 1,
            lastDoneDate = "2026-05-27",
            completedTaskIds = setOf(" home_001 ", " "),
        )

        val next = progress.withCompletedTask(" home_002 ", today)

        assertEquals(3, next.totalDone)
        assertEquals(setOf("home_001", "home_002"), next.completedTaskIds)
    }
}
