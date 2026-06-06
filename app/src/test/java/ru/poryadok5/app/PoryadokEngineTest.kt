package ru.poryadok5.app

import ru.poryadok5.app.domain.EnergyLevel
import ru.poryadok5.app.domain.MicroTask
import ru.poryadok5.app.domain.PoryadokEngine
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.TaskFilter
import ru.poryadok5.app.domain.TaskSuggestionQuality
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDate

class PoryadokEngineTest {
    private val tasks = listOf(
        task("home_light_3", TaskArea.Home, EnergyLevel.Light, 3),
        task("home_medium_3", TaskArea.Home, EnergyLevel.Medium, 3),
        task("home_active_5", TaskArea.Home, EnergyLevel.Active, 5),
        task("work_light_3", TaskArea.Work, EnergyLevel.Light, 3),
        task("digital_light_10", TaskArea.Digital, EnergyLevel.Light, 10),
    )

    @Test
    fun suggestTaskPrefersExactFilterMatch() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(filter, completedIds = emptySet(), day = LocalDate.of(2026, 5, 28))

        assertEquals("home_light_3", suggestion.id)
    }

    @Test
    fun suggestTaskSkipsCompletedExactMatchWhenAlternativeInRelaxedPoolExists() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = setOf("home_light_3"),
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals(TaskArea.Home, suggestion.area)
        assertEquals(3, suggestion.minutes)
        assertEquals("home_medium_3", suggestion.id)
    }

    @Test
    fun suggestTaskTrimsCompletedIdsBeforeExcludingTasks() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = setOf(" home_light_3 "),
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_medium_3", suggestion.id)
    }

    @Test
    fun suggestTaskAvoidsExcludedIdsWhenAlternativeExists() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = emptySet(),
            excludedIds = setOf("home_light_3"),
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_medium_3", suggestion.id)
    }

    @Test
    fun suggestTaskTrimsExcludedIdsBeforeSkippingTasks() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = emptySet(),
            excludedIds = setOf(" home_light_3 "),
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_medium_3", suggestion.id)
    }

    @Test
    fun suggestTaskFallsBackWhenExcludedIdsExhaustAvailableTasks() {
        val engine = PoryadokEngine(listOf(task("home_light_3", TaskArea.Home, EnergyLevel.Light, 3)))
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = emptySet(),
            excludedIds = setOf("home_light_3"),
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_light_3", suggestion.id)
    }

    @Test
    fun hasAlternativeSuggestionDetectsAnotherTaskAfterSkippingCurrent() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        assertTrue(
            engine.hasAlternativeSuggestion(
                filter = filter,
                completedIds = emptySet(),
                excludedIds = emptySet(),
                currentTaskId = "home_light_3",
                day = LocalDate.of(2026, 5, 28),
            ),
        )
    }

    @Test
    fun hasAlternativeSuggestionReturnsFalseForSingleTaskCatalog() {
        val engine = PoryadokEngine(listOf(task("home_light_3", TaskArea.Home, EnergyLevel.Light, 3)))
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        assertFalse(
            engine.hasAlternativeSuggestion(
                filter = filter,
                completedIds = emptySet(),
                excludedIds = emptySet(),
                currentTaskId = "home_light_3",
                day = LocalDate.of(2026, 5, 28),
            ),
        )
    }

    @Test
    fun suggestTaskNormalizesUnsupportedFilterMinutes() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Active, 7)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = emptySet(),
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_active_5", suggestion.id)
    }

    @Test
    fun suggestTaskFallsBackToWholeCatalogWhenAreaAndDurationAreExhausted() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestTask(
            filter = filter,
            completedIds = setOf("home_light_3", "home_medium_3"),
            day = LocalDate.of(2026, 5, 28),
        )

        assertFalse(suggestion.id in setOf("home_light_3", "home_medium_3"))
        assertTrue(suggestion.id in tasks.map { it.id })
    }

    @Test
    fun suggestionQualityIdentifiesExactFilterMatch() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val quality = engine.suggestionQuality(filter, tasks.first { it.id == "home_light_3" })

        assertEquals(TaskSuggestionQuality.Exact, quality)
    }

    @Test
    fun suggestionQualityIdentifiesAreaAndDurationFallback() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val quality = engine.suggestionQuality(filter, tasks.first { it.id == "home_medium_3" })

        assertEquals(TaskSuggestionQuality.AreaAndDuration, quality)
    }

    @Test
    fun suggestionQualityIdentifiesWholeCatalogFallback() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val quality = engine.suggestionQuality(filter, tasks.first { it.id == "work_light_3" })

        assertEquals(TaskSuggestionQuality.CatalogFallback, quality)
    }

    @Test
    fun suggestionQualityNormalizesUnsupportedFilterMinutes() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Active, 7)

        val quality = engine.suggestionQuality(filter, tasks.first { it.id == "home_active_5" })

        assertEquals(TaskSuggestionQuality.Exact, quality)
    }

    @Test
    fun suggestAfterCompletionExcludesJustCompletedTask() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestAfterCompletion(
            filter = filter,
            completedIds = emptySet(),
            completedTaskId = "home_light_3",
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_medium_3", suggestion.id)
    }

    @Test
    fun suggestAfterCompletionTrimsJustCompletedTaskId() {
        val engine = PoryadokEngine(tasks)
        val filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3)

        val suggestion = engine.suggestAfterCompletion(
            filter = filter,
            completedIds = emptySet(),
            completedTaskId = " home_light_3 ",
            day = LocalDate.of(2026, 5, 28),
        )

        assertEquals("home_medium_3", suggestion.id)
    }

    @Test
    fun progressCountsOnlyKnownCatalogTaskIds() {
        val engine = PoryadokEngine(tasks)

        assertEquals(2, engine.completedCount(setOf("home_light_3", "missing_999", "work_light_3")))
        assertEquals(40, engine.progressPercent(setOf("home_light_3", "missing_999", "work_light_3")))
    }

    @Test
    fun progressCountTrimsCompletedIdsBeforeCatalogMatch() {
        val engine = PoryadokEngine(tasks)

        assertEquals(2, engine.completedCount(setOf(" home_light_3 ", " missing_999 ", "work_light_3")))
        assertEquals(40, engine.progressPercent(setOf(" home_light_3 ", " missing_999 ", "work_light_3")))
    }

    @Test
    fun completedCountByAreaUsesKnownTrimmedCatalogIds() {
        val engine = PoryadokEngine(tasks)

        val completedIds = setOf(" home_light_3 ", "home_medium_3", "work_light_3", "missing_999")

        assertEquals(2, engine.completedCountByArea(TaskArea.Home, completedIds))
        assertEquals(1, engine.completedCountByArea(TaskArea.Work, completedIds))
        assertEquals(0, engine.completedCountByArea(TaskArea.Digital, completedIds))
    }

    @Test
    fun nextFocusAreaPrefersLeastCompletedUnfinishedArea() {
        val engine = PoryadokEngine(tasks)

        assertEquals(TaskArea.Work, engine.nextFocusArea(setOf("home_light_3")))
        assertEquals(TaskArea.Digital, engine.nextFocusArea(setOf("home_light_3", " work_light_3 ")))
    }

    @Test
    fun nextFocusAreaReturnsNullWhenCatalogIsComplete() {
        val engine = PoryadokEngine(tasks)

        assertEquals(null, engine.nextFocusArea(tasks.mapTo(mutableSetOf()) { it.id } + "missing_999"))
    }

    @Test
    fun hasUncompletedTasksAfterCompletionUsesKnownTrimmedCatalogIds() {
        val engine = PoryadokEngine(tasks)
        val allButOne = tasks.mapTo(mutableSetOf()) { it.id } - "home_light_3" + " missing_999 "

        assertTrue(engine.hasUncompletedTasksAfterCompletion(allButOne, " missing_999 "))
        assertFalse(engine.hasUncompletedTasksAfterCompletion(allButOne, " home_light_3 "))
    }

    @Test
    fun emptyCatalogHasZeroProgressAndNoTaskSuggestion() {
        val engine = PoryadokEngine(emptyList())

        assertEquals(0, engine.totalTasks())
        assertEquals(0, engine.progressPercent(setOf("missing_999")))
        assertEquals(0, engine.completedCount(setOf("missing_999")))
        assertFalse(engine.hasUncompletedTasksAfterCompletion(setOf("missing_999"), "home_light_3"))
        assertEquals(0, engine.completedCountByArea(TaskArea.Home, setOf("home_light_3")))
        assertEquals(null, engine.nextFocusArea(setOf("home_light_3")))
        assertFailsWithMessage("Task catalog must contain at least one task.") {
            engine.suggestTask(
                filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 3),
                completedIds = emptySet(),
                day = LocalDate.of(2026, 5, 28),
            )
        }
    }
}

private fun task(
    id: String,
    area: TaskArea,
    energy: EnergyLevel,
    minutes: Int,
): MicroTask {
    return MicroTask(
        id = id,
        area = area,
        energy = energy,
        minutes = minutes,
        title = "Тестовая задача $id",
        steps = listOf("Шаг один", "Шаг два"),
        resultText = "Готово",
    )
}

private fun assertFailsWithMessage(message: String, block: () -> Unit) {
    val failure = runCatching(block).exceptionOrNull()
    assertTrue("Expected failure with message: $message", failure is IllegalStateException)
    assertEquals(message, failure?.message)
}
