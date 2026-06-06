package ru.poryadok5.app.data

import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.mutablePreferencesOf
import androidx.datastore.preferences.core.preferencesOf
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.UserProgress
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class UserPreferencesRepositoryTest {
    @Test
    fun emptyPreferencesMapToAppDefaults() {
        val preferences = emptyPreferences().toAppPreferences()

        assertFalse(preferences.settings.onboardingDone)
        assertEquals(TaskArea.Home, preferences.settings.preferredArea)
        assertTrue(preferences.settings.hapticsEnabled)
        assertEquals(UserProgress(), preferences.progress)
    }

    @Test
    fun storedPreferencesMapToAppPreferences() {
        val rawPreferences = preferencesOf(
            UserPreferencesKeys.OnboardingDone to true,
            UserPreferencesKeys.PreferredArea to TaskArea.Digital.name,
            UserPreferencesKeys.HapticsEnabled to false,
            UserPreferencesKeys.TotalDone to 12,
            UserPreferencesKeys.StreakDays to 4,
            UserPreferencesKeys.LastDoneDate to "2026-05-27",
            UserPreferencesKeys.CompletedTaskIds to setOf("home_001", "digital_002"),
        )

        val preferences = rawPreferences.toAppPreferences()

        assertTrue(preferences.settings.onboardingDone)
        assertEquals(TaskArea.Digital, preferences.settings.preferredArea)
        assertFalse(preferences.settings.hapticsEnabled)
        assertEquals(12, preferences.progress.totalDone)
        assertEquals(4, preferences.progress.streakDays)
        assertEquals("2026-05-27", preferences.progress.lastDoneDate)
        assertEquals(setOf("home_001", "digital_002"), preferences.progress.completedTaskIds)
    }

    @Test
    fun unknownStoredAreaFallsBackToHome() {
        val rawPreferences = preferencesOf(
            UserPreferencesKeys.PreferredArea to "ArchivedArea",
        )

        val preferences = rawPreferences.toAppPreferences()

        assertEquals(TaskArea.Home, preferences.settings.preferredArea)
    }

    @Test
    fun storedPreferredAreaIsTrimmedForUi() {
        val rawPreferences = preferencesOf(
            UserPreferencesKeys.PreferredArea to " digital ",
        )

        val preferences = rawPreferences.toAppPreferences()

        assertEquals(TaskArea.Digital, preferences.settings.preferredArea)
    }

    @Test
    fun corruptedStoredProgressIsNormalizedForUi() {
        val rawPreferences = preferencesOf(
            UserPreferencesKeys.TotalDone to -7,
            UserPreferencesKeys.StreakDays to -2,
            UserPreferencesKeys.LastDoneDate to "bad-date",
            UserPreferencesKeys.CompletedTaskIds to setOf("", " home_001 ", " "),
        )

        val preferences = rawPreferences.toAppPreferences()

        assertEquals(0, preferences.progress.totalDone)
        assertEquals(0, preferences.progress.streakDays)
        assertNull(preferences.progress.lastDoneDate)
        assertEquals(setOf("home_001"), preferences.progress.completedTaskIds)
    }

    @Test
    fun storedLastDoneDateIsTrimmedForUi() {
        val rawPreferences = preferencesOf(
            UserPreferencesKeys.LastDoneDate to " 2026-05-27 ",
        )

        val preferences = rawPreferences.toAppPreferences()

        assertEquals("2026-05-27", preferences.progress.lastDoneDate)
    }

    @Test
    fun writeProgressStoresProgressFields() {
        val rawPreferences = mutablePreferencesOf()

        rawPreferences.writeProgress(
            UserProgress(
                totalDone = 3,
                streakDays = 2,
                lastDoneDate = "2026-05-27",
                completedTaskIds = setOf("home_001", "work_002"),
            ),
        )

        assertEquals(3, rawPreferences[UserPreferencesKeys.TotalDone])
        assertEquals(2, rawPreferences[UserPreferencesKeys.StreakDays])
        assertEquals("2026-05-27", rawPreferences[UserPreferencesKeys.LastDoneDate])
        assertEquals(setOf("home_001", "work_002"), rawPreferences[UserPreferencesKeys.CompletedTaskIds])
    }

    @Test
    fun writeProgressRemovesBlankLastDoneDate() {
        val rawPreferences = mutablePreferencesOf(
            UserPreferencesKeys.LastDoneDate to "2026-05-27",
        )

        rawPreferences.writeProgress(UserProgress(lastDoneDate = ""))

        assertNull(rawPreferences[UserPreferencesKeys.LastDoneDate])
    }

    @Test
    fun writeProgressNormalizesLastDoneDateBeforeStorage() {
        val rawPreferences = mutablePreferencesOf()

        rawPreferences.writeProgress(UserProgress(lastDoneDate = " 2026-05-27 "))

        assertEquals("2026-05-27", rawPreferences[UserPreferencesKeys.LastDoneDate])
    }

    @Test
    fun writeProgressRemovesMalformedLastDoneDate() {
        val rawPreferences = mutablePreferencesOf(
            UserPreferencesKeys.LastDoneDate to "2026-05-27",
        )

        rawPreferences.writeProgress(UserProgress(lastDoneDate = "bad-date"))

        assertNull(rawPreferences[UserPreferencesKeys.LastDoneDate])
    }

    @Test
    fun writeProgressNormalizesInvalidProgressBeforeStorage() {
        val rawPreferences = mutablePreferencesOf()

        rawPreferences.writeProgress(
            UserProgress(
                totalDone = -5,
                streakDays = -4,
                completedTaskIds = setOf("", "home_001", " work_002 ", " "),
            ),
        )

        assertEquals(0, rawPreferences[UserPreferencesKeys.TotalDone])
        assertEquals(0, rawPreferences[UserPreferencesKeys.StreakDays])
        assertEquals(setOf("home_001", "work_002"), rawPreferences[UserPreferencesKeys.CompletedTaskIds])
    }
}
