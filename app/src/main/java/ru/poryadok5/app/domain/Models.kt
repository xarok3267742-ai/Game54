package ru.poryadok5.app.domain

data class MicroTask(
    val id: String,
    val area: TaskArea,
    val energy: EnergyLevel,
    val minutes: Int,
    val title: String,
    val steps: List<String>,
    val resultText: String,
)

enum class TaskArea(val label: String, val shortLabel: String) {
    Home("Дом", "Дом"),
    Work("Рабочее место", "Работа"),
    Digital("Цифровой порядок", "Цифра"),
    Kitchen("Кухня", "Кухня"),
    Personal("Личные вещи", "Вещи");

    companion object {
        fun fromRaw(value: String): TaskArea {
            val normalized = value.trim()
            return entries.firstOrNull { it.name.equals(normalized, ignoreCase = true) } ?: Home
        }
    }
}

enum class EnergyLevel(val label: String, val helper: String) {
    Light("Лёгкая", "без усилия"),
    Medium("Средняя", "спокойный фокус"),
    Active("Бодрая", "быстро и заметно");

    companion object {
        fun fromRaw(value: String): EnergyLevel {
            val normalized = value.trim()
            return entries.firstOrNull { it.name.equals(normalized, ignoreCase = true) } ?: Light
        }
    }
}

data class UserProgress(
    val totalDone: Int = 0,
    val streakDays: Int = 0,
    val lastDoneDate: String? = null,
    val completedTaskIds: Set<String> = emptySet(),
)

data class AppSettings(
    val onboardingDone: Boolean = false,
    val preferredArea: TaskArea = TaskArea.Home,
    val hapticsEnabled: Boolean = true,
)

data class AppPreferences(
    val settings: AppSettings = AppSettings(),
    val progress: UserProgress = UserProgress(),
)

val SupportedTaskMinutes = setOf(3, 5, 10)
val SupportedTaskIdPattern = Regex("^(home|work|digital|kitchen|personal)_[0-9]{3}$")

fun normalizedTaskMinutes(value: Int): Int {
    return if (value in SupportedTaskMinutes) value else 5
}

fun isRouteSafeTaskId(value: String): Boolean {
    return SupportedTaskIdPattern.matches(value)
}

data class TaskFilter(
    val area: TaskArea,
    val energy: EnergyLevel,
    val minutes: Int,
)

enum class TaskSuggestionQuality {
    Exact,
    AreaAndDuration,
    CatalogFallback,
}
