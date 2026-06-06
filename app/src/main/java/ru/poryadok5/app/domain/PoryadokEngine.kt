package ru.poryadok5.app.domain

import java.time.LocalDate

class PoryadokEngine(
    private val tasks: List<MicroTask>,
) {
    private val taskIds: Set<String> = tasks.mapTo(mutableSetOf()) { it.id }

    fun suggestTask(
        filter: TaskFilter,
        completedIds: Set<String>,
        excludedIds: Set<String> = emptySet(),
        day: LocalDate = LocalDate.now(),
    ): MicroTask {
        val normalizedFilter = filter.copy(minutes = normalizedTaskMinutes(filter.minutes))
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)
        val normalizedExcludedIds = normalizedCompletedTaskIds(excludedIds)
        val exact = tasks.filter {
            it.area == normalizedFilter.area &&
                it.energy == normalizedFilter.energy &&
                it.minutes == normalizedFilter.minutes
        }
        val relaxed = tasks.filter {
            it.area == normalizedFilter.area && it.minutes == normalizedFilter.minutes
        }
        val pools = listOf(exact, relaxed, tasks).filter { it.isNotEmpty() }
        val source = pools
            .asSequence()
            .map { pool -> pool.filterNot { it.id in normalizedCompletedIds || it.id in normalizedExcludedIds } }
            .firstOrNull { it.isNotEmpty() }
            ?: pools
                .asSequence()
                .map { pool -> pool.filterNot { it.id in normalizedCompletedIds } }
                .firstOrNull { it.isNotEmpty() }
            ?: pools.firstOrNull()
            ?: error("Task catalog must contain at least one task.")
        val stableIndex = day.toEpochDay() +
            normalizedFilter.area.ordinal * 17L +
            normalizedFilter.energy.ordinal * 31L +
            normalizedFilter.minutes
        return source[Math.floorMod(stableIndex, source.size.toLong()).toInt()]
    }

    fun hasAlternativeSuggestion(
        filter: TaskFilter,
        completedIds: Set<String>,
        excludedIds: Set<String>,
        currentTaskId: String,
        day: LocalDate = LocalDate.now(),
    ): Boolean {
        if (tasks.size <= 1) return false
        val normalizedCurrentTaskId = currentTaskId.trim()
        return suggestTask(
            filter = filter,
            completedIds = completedIds,
            excludedIds = excludedIds + normalizedCurrentTaskId,
            day = day,
        ).id != normalizedCurrentTaskId
    }

    fun suggestAfterCompletion(
        filter: TaskFilter,
        completedIds: Set<String>,
        completedTaskId: String,
        day: LocalDate = LocalDate.now(),
    ): MicroTask {
        return suggestTask(filter, normalizedCompletedTaskIds(completedIds + completedTaskId), day = day)
    }

    fun progressPercent(completedIds: Set<String>): Int {
        if (tasks.isEmpty()) return 0
        return ((completedCount(completedIds) * 100f) / tasks.size).toInt()
    }

    fun totalTasks(): Int = tasks.size

    fun completedCount(completedIds: Set<String>): Int = normalizedCompletedTaskIds(completedIds).count { it in taskIds }

    fun hasUncompletedTasksAfterCompletion(completedIds: Set<String>, completedTaskId: String): Boolean {
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds + completedTaskId)
        return tasks.any { it.id !in normalizedCompletedIds }
    }

    fun completedCountByArea(area: TaskArea, completedIds: Set<String>): Int {
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)
        return tasks.count { it.area == area && it.id in normalizedCompletedIds }
    }

    fun countByArea(area: TaskArea): Int = tasks.count { it.area == area }

    fun nextFocusArea(completedIds: Set<String>): TaskArea? {
        val normalizedCompletedIds = normalizedCompletedTaskIds(completedIds)
        return TaskArea.entries
            .mapNotNull { area ->
                val total = countByArea(area)
                if (total == 0) {
                    null
                } else {
                    val completed = tasks.count { it.area == area && it.id in normalizedCompletedIds }
                    AreaProgress(area = area, completed = completed, total = total)
                }
            }
            .filter { it.completed < it.total }
            .minWithOrNull(
                compareBy<AreaProgress> { it.completed.toFloat() / it.total.toFloat() }
                    .thenBy { it.completed }
                    .thenBy { it.area.ordinal },
            )
            ?.area
    }

    fun suggestionQuality(filter: TaskFilter, task: MicroTask): TaskSuggestionQuality {
        val normalizedFilter = filter.copy(minutes = normalizedTaskMinutes(filter.minutes))
        return when {
            task.area == normalizedFilter.area &&
                task.energy == normalizedFilter.energy &&
                task.minutes == normalizedFilter.minutes -> TaskSuggestionQuality.Exact

            task.area == normalizedFilter.area &&
                task.minutes == normalizedFilter.minutes -> TaskSuggestionQuality.AreaAndDuration

            else -> TaskSuggestionQuality.CatalogFallback
        }
    }

    private data class AreaProgress(
        val area: TaskArea,
        val completed: Int,
        val total: Int,
    )
}
