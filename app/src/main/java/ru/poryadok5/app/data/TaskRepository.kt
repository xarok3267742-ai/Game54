package ru.poryadok5.app.data

import android.content.Context
import ru.poryadok5.app.R
import ru.poryadok5.app.domain.EnergyLevel
import ru.poryadok5.app.domain.MicroTask
import ru.poryadok5.app.domain.SupportedTaskMinutes
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.isRouteSafeTaskId
import org.json.JSONArray

class TaskRepository(
    private val context: Context,
) {
    fun loadTasks(): List<MicroTask> {
        val json = context.resources.openRawResource(R.raw.tasks_ru)
            .bufferedReader()
            .use { it.readText() }
        return parseTaskCatalog(json)
    }
}

internal fun parseTaskCatalog(json: String): List<MicroTask> {
    val items = JSONArray(json)
    val ids = mutableSetOf<String>()
    val tasks = buildList {
        for (index in 0 until items.length()) {
            val item = items.getJSONObject(index)
            val id = parseTaskId(item.getString("id"))
            val area = parseCatalogArea(item.getString("area"), id)
            validateTaskIdArea(id, area)
            require(ids.add(id)) { "Повторяющийся id задачи $id." }
            add(
                MicroTask(
                    id = id,
                    area = area,
                    energy = parseCatalogEnergy(item.getString("energy"), id),
                    minutes = parseTaskMinutes(item.getInt("minutes"), id),
                    title = parseRequiredText(item.getString("title"), id, "название"),
                    steps = parseTaskSteps(item.getJSONArray("steps"), id),
                    resultText = parseRequiredText(item.getString("resultText"), id, "результат"),
                ),
            )
        }
    }

    require(tasks.isNotEmpty()) { "Локальный список задач пуст." }
    return tasks
}

private fun parseTaskId(value: String): String {
    val id = value.trim()
    require(id.isNotEmpty()) { "Задача должна содержать id." }
    require(isRouteSafeTaskId(id)) { "Задача $id содержит неподдерживаемый id." }
    return id
}

private fun validateTaskIdArea(id: String, area: TaskArea) {
    require(id.startsWith("${area.catalogIdPrefix()}_")) { "Id задачи $id не соответствует зоне ${area.label}." }
}

private fun TaskArea.catalogIdPrefix(): String {
    return when (this) {
        TaskArea.Home -> "home"
        TaskArea.Work -> "work"
        TaskArea.Digital -> "digital"
        TaskArea.Kitchen -> "kitchen"
        TaskArea.Personal -> "personal"
    }
}

private fun parseCatalogArea(value: String, taskId: String): TaskArea {
    return TaskArea.entries.firstOrNull { it.name == value }
        ?: throw IllegalArgumentException("Неизвестная зона задачи $taskId.")
}

private fun parseCatalogEnergy(value: String, taskId: String): EnergyLevel {
    return EnergyLevel.entries.firstOrNull { it.name == value }
        ?: throw IllegalArgumentException("Неизвестный уровень энергии задачи $taskId.")
}

private fun parseRequiredText(value: String, taskId: String, label: String): String {
    val normalized = value.trim()
    require(normalized.isNotEmpty()) { "Задача $taskId должна содержать $label." }
    return normalized
}

private fun parseTaskMinutes(value: Int, taskId: String): Int {
    require(value in SupportedTaskMinutes) { "Задача $taskId содержит неподдерживаемое время." }
    return value
}

private fun parseTaskSteps(stepsJson: org.json.JSONArray, taskId: String): List<String> {
    require(stepsJson.length() == 3) { "Задача $taskId должна содержать ровно 3 шага." }
    return buildList {
        for (stepIndex in 0 until stepsJson.length()) {
            val step = stepsJson.getString(stepIndex).trim()
            require(step.isNotEmpty()) { "Задача $taskId содержит пустой шаг." }
            add(step)
        }
    }
}
