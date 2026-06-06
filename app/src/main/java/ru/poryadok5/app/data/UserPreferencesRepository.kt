package ru.poryadok5.app.data

import android.content.Context
import androidx.datastore.preferences.core.MutablePreferences
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import ru.poryadok5.app.domain.AppPreferences
import ru.poryadok5.app.domain.AppSettings
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.UserProgress
import ru.poryadok5.app.domain.normalizedCompletedTaskIds
import ru.poryadok5.app.domain.normalizedLastDoneDate
import ru.poryadok5.app.domain.withCompletedTask
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import java.io.IOException
import java.time.LocalDate

private val Context.userDataStore by preferencesDataStore(name = "poryadok5_user")

class UserPreferencesRepository(
    private val context: Context,
) {
    val preferences: Flow<AppPreferences> = context.userDataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { prefs -> prefs.toAppPreferences() }

    suspend fun completeOnboarding(preferredArea: TaskArea) {
        context.userDataStore.edit { prefs ->
            prefs[UserPreferencesKeys.OnboardingDone] = true
            prefs[UserPreferencesKeys.PreferredArea] = preferredArea.name
        }
    }

    suspend fun setPreferredArea(area: TaskArea) {
        context.userDataStore.edit { prefs ->
            prefs[UserPreferencesKeys.PreferredArea] = area.name
        }
    }

    suspend fun setHapticsEnabled(enabled: Boolean) {
        context.userDataStore.edit { prefs ->
            prefs[UserPreferencesKeys.HapticsEnabled] = enabled
        }
    }

    suspend fun recordCompletion(taskId: String, today: LocalDate = LocalDate.now()) {
        context.userDataStore.edit { prefs ->
            prefs.writeProgress(prefs.toAppPreferences().progress.withCompletedTask(taskId, today))
        }
    }

    suspend fun resetProgress() {
        context.userDataStore.edit { prefs ->
            prefs[UserPreferencesKeys.TotalDone] = 0
            prefs[UserPreferencesKeys.StreakDays] = 0
            prefs.remove(UserPreferencesKeys.LastDoneDate)
            prefs[UserPreferencesKeys.CompletedTaskIds] = emptySet()
        }
    }
}

internal fun Preferences.toAppPreferences(): AppPreferences {
    return AppPreferences(
        settings = AppSettings(
            onboardingDone = this[UserPreferencesKeys.OnboardingDone] ?: false,
            preferredArea = this[UserPreferencesKeys.PreferredArea]?.let(TaskArea::fromRaw) ?: TaskArea.Home,
            hapticsEnabled = this[UserPreferencesKeys.HapticsEnabled] ?: true,
        ),
        progress = UserProgress(
            totalDone = (this[UserPreferencesKeys.TotalDone] ?: 0).coerceAtLeast(0),
            streakDays = (this[UserPreferencesKeys.StreakDays] ?: 0).coerceAtLeast(0),
            lastDoneDate = normalizedLastDoneDate(this[UserPreferencesKeys.LastDoneDate]),
            completedTaskIds = this[UserPreferencesKeys.CompletedTaskIds]
                ?.let(::normalizedCompletedTaskIds)
                ?: emptySet(),
        ),
    )
}

internal fun MutablePreferences.writeProgress(progress: UserProgress) {
    this[UserPreferencesKeys.TotalDone] = progress.totalDone.coerceAtLeast(0)
    this[UserPreferencesKeys.StreakDays] = progress.streakDays.coerceAtLeast(0)
    normalizedLastDoneDate(progress.lastDoneDate)?.let { lastDoneDate ->
        this[UserPreferencesKeys.LastDoneDate] = lastDoneDate
    } ?: remove(UserPreferencesKeys.LastDoneDate)
    this[UserPreferencesKeys.CompletedTaskIds] = normalizedCompletedTaskIds(progress.completedTaskIds)
}

internal object UserPreferencesKeys {
    val OnboardingDone = booleanPreferencesKey("onboarding_done")
    val PreferredArea = stringPreferencesKey("preferred_area")
    val HapticsEnabled = booleanPreferencesKey("haptics_enabled")
    val TotalDone = intPreferencesKey("total_done")
    val StreakDays = intPreferencesKey("streak_days")
    val LastDoneDate = stringPreferencesKey("last_done_date")
    val CompletedTaskIds = stringSetPreferencesKey("completed_task_ids")
}
