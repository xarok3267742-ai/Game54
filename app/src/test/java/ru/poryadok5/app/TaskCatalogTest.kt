package ru.poryadok5.app

import ru.poryadok5.app.domain.EnergyLevel
import ru.poryadok5.app.domain.MicroTask
import ru.poryadok5.app.domain.PoryadokEngine
import ru.poryadok5.app.domain.SupportedTaskMinutes
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.TaskFilter
import ru.poryadok5.app.data.parseTaskCatalog
import org.json.JSONArray
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class TaskCatalogTest {
    private val validTaskJson = """
        [
          {
            "id": "home_001",
            "area": "Home",
            "energy": "Light",
            "minutes": 5,
            "title": "Быстрая полка",
            "steps": ["Уберите лишнее", "Протрите поверхность", "Верните нужное"],
            "resultText": "Полка выглядит спокойнее."
          }
        ]
    """.trimIndent()

    @Test
    fun taskCatalogHasCompleteMvpContent() {
        val catalog = JSONArray(File("src/main/res/raw/tasks_ru.json").readText())

        assertEquals(80, catalog.length())

        val ids = mutableSetOf<String>()
        val areaCounts = mutableMapOf<String, Int>()
        val unsupportedMinutes = mutableListOf<Int>()
        val forbiddenTokens = listOf("TO" + "DO", "FIX" + "ME", "Lor" + "em", "place" + "holder", "Hello" + " world")

        for (index in 0 until catalog.length()) {
            val item = catalog.getJSONObject(index)
            val id = item.getString("id")
            val title = item.getString("title")
            val result = item.getString("resultText")
            val steps = item.getJSONArray("steps")

            assertTrue("Duplicate task id: $id", ids.add(id))
            assertTrue("Title should contain Cyrillic text: $title", title.any { it in 'А'..'я' || it == 'ё' || it == 'Ё' })
            assertTrue("Result should be useful: $id", result.length >= 24)
            assertTrue("Task should have at least three steps: $id", steps.length() >= 3)
            assertTrue("Unknown area: $id", item.getString("area") in TaskArea.entries.map { it.name })
            assertTrue("Unknown energy: $id", item.getString("energy") in EnergyLevel.entries.map { it.name })

            val minutes = item.getInt("minutes")
            if (minutes !in SupportedTaskMinutes) {
                unsupportedMinutes += minutes
            }
            areaCounts[item.getString("area")] = areaCounts.getOrDefault(item.getString("area"), 0) + 1

            val combined = buildString {
                append(title)
                append(result)
                for (stepIndex in 0 until steps.length()) append(steps.getString(stepIndex))
            }
            forbiddenTokens.forEach { token ->
                assertFalse("$id contains forbidden token $token", combined.contains(token, ignoreCase = true))
            }
        }

        assertTrue("Unsupported minute values: $unsupportedMinutes", unsupportedMinutes.isEmpty())
        TaskArea.entries.forEach { area ->
            assertEquals("Each area should have 16 tasks", 16, areaCounts[area.name])
        }
    }

    @Test
    fun engineSuggestsUncompletedTaskWhenPossible() {
        val tasks = listOf(
            MicroTask("a", TaskArea.Home, EnergyLevel.Light, 5, "Первая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("b", TaskArea.Home, EnergyLevel.Light, 5, "Вторая задача", listOf("Один", "Два", "Три"), "Готово"),
        )
        val engine = PoryadokEngine(tasks)

        val suggestion = engine.suggestTask(
            filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 5),
            completedIds = setOf("a"),
        )

        assertEquals("b", suggestion.id)
    }

    @Test
    fun engineSuggestsNextTaskAfterJustCompletedTask() {
        val tasks = listOf(
            MicroTask("a", TaskArea.Home, EnergyLevel.Light, 5, "Первая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("b", TaskArea.Home, EnergyLevel.Light, 5, "Вторая задача", listOf("Один", "Два", "Три"), "Готово"),
        )
        val engine = PoryadokEngine(tasks)

        val suggestion = engine.suggestAfterCompletion(
            filter = TaskFilter(TaskArea.Home, EnergyLevel.Light, 5),
            completedIds = emptySet(),
            completedTaskId = "a",
        )

        assertEquals("b", suggestion.id)
    }

    @Test
    fun engineAvoidsImmediateRepeatByRelaxingEnergyWhenExactBucketIsDone() {
        val tasks = listOf(
            MicroTask("a", TaskArea.Home, EnergyLevel.Active, 3, "Первая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("b", TaskArea.Home, EnergyLevel.Light, 3, "Вторая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("c", TaskArea.Work, EnergyLevel.Active, 3, "Третья задача", listOf("Один", "Два", "Три"), "Готово"),
        )
        val engine = PoryadokEngine(tasks)

        val suggestion = engine.suggestAfterCompletion(
            filter = TaskFilter(TaskArea.Home, EnergyLevel.Active, 3),
            completedIds = emptySet(),
            completedTaskId = "a",
        )

        assertEquals("b", suggestion.id)
    }

    @Test
    fun progressIgnoresUnknownCompletedIds() {
        val tasks = listOf(
            MicroTask("a", TaskArea.Home, EnergyLevel.Light, 5, "Первая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("b", TaskArea.Home, EnergyLevel.Light, 5, "Вторая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("c", TaskArea.Home, EnergyLevel.Light, 5, "Третья задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("d", TaskArea.Home, EnergyLevel.Light, 5, "Четвёртая задача", listOf("Один", "Два", "Три"), "Готово"),
        )
        val engine = PoryadokEngine(tasks)

        val completedIds = setOf("a", "unknown_001", "unknown_002")

        assertEquals(1, engine.completedCount(completedIds))
        assertEquals(25, engine.progressPercent(completedIds))
    }

    @Test
    fun engineReportsCatalogSizeForRuntimeUi() {
        val tasks = listOf(
            MicroTask("a", TaskArea.Home, EnergyLevel.Light, 5, "Первая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("b", TaskArea.Work, EnergyLevel.Medium, 10, "Вторая задача", listOf("Один", "Два", "Три"), "Готово"),
            MicroTask("c", TaskArea.Digital, EnergyLevel.Active, 3, "Третья задача", listOf("Один", "Два", "Три"), "Готово"),
        )
        val engine = PoryadokEngine(tasks)

        assertEquals(3, engine.totalTasks())
    }

    @Test
    fun taskParserLoadsValidCatalog() {
        val tasks = parseTaskCatalog(validTaskJson)

        assertEquals(1, tasks.size)
        assertEquals(TaskArea.Home, tasks.single().area)
        assertEquals(EnergyLevel.Light, tasks.single().energy)
        assertEquals(listOf("Уберите лишнее", "Протрите поверхность", "Верните нужное"), tasks.single().steps)
    }

    @Test
    fun taskParserRejectsEmptyCatalog() {
        val failure = runCatching { parseTaskCatalog("[]") }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Локальный список задач пуст.", failure?.message)
    }

    @Test
    fun taskParserRejectsUnknownAreaInsteadOfFallingBack() {
        val json = validTaskJson.replace("\"area\": \"Home\"", "\"area\": \"ArchivedArea\"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Неизвестная зона задачи home_001.", failure?.message)
    }

    @Test
    fun taskParserRejectsUnknownEnergyInsteadOfFallingBack() {
        val json = validTaskJson.replace("\"energy\": \"Light\"", "\"energy\": \"Extreme\"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Неизвестный уровень энергии задачи home_001.", failure?.message)
    }

    @Test
    fun taskParserRejectsBlankId() {
        val json = validTaskJson.replace("\"id\": \"home_001\"", "\"id\": \"   \"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача должна содержать id.", failure?.message)
    }

    @Test
    fun taskParserRejectsRouteUnsafeId() {
        val json = validTaskJson.replace("\"id\": \"home_001\"", "\"id\": \"home:001\"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача home:001 содержит неподдерживаемый id.", failure?.message)
    }

    @Test
    fun taskParserRejectsIdAreaMismatch() {
        val json = validTaskJson.replace("\"area\": \"Home\"", "\"area\": \"Work\"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Id задачи home_001 не соответствует зоне Рабочее место.", failure?.message)
    }

    @Test
    fun taskParserRejectsDuplicateIds() {
        val json = """
            [
              {
                "id": "home_001",
                "area": "Home",
                "energy": "Light",
                "minutes": 5,
                "title": "Быстрая полка",
                "steps": ["Уберите лишнее", "Протрите поверхность", "Верните нужное"],
                "resultText": "Полка выглядит спокойнее."
              },
              {
                "id": "home_001",
                "area": "Home",
                "energy": "Medium",
                "minutes": 10,
                "title": "Тихий стол",
                "steps": ["Соберите бумаги", "Оставьте нужное", "Протрите место"],
                "resultText": "Стол стал спокойнее."
              }
            ]
        """.trimIndent()

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Повторяющийся id задачи home_001.", failure?.message)
    }

    @Test
    fun taskParserRejectsUnsupportedMinutes() {
        val json = validTaskJson.replace("\"minutes\": 5", "\"minutes\": 7")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача home_001 содержит неподдерживаемое время.", failure?.message)
    }

    @Test
    fun taskParserRejectsBlankTitle() {
        val json = validTaskJson.replace("\"title\": \"Быстрая полка\"", "\"title\": \"   \"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача home_001 должна содержать название.", failure?.message)
    }

    @Test
    fun taskParserRejectsWrongStepCountBeforeUiCanReadFirstStep() {
        val json = validTaskJson.replace(
            "\"steps\": [\"Уберите лишнее\", \"Протрите поверхность\", \"Верните нужное\"]",
            "\"steps\": []",
        )

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача home_001 должна содержать ровно 3 шага.", failure?.message)
    }

    @Test
    fun taskParserRejectsBlankStep() {
        val json = validTaskJson.replace("\"Протрите поверхность\"", "\"   \"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача home_001 содержит пустой шаг.", failure?.message)
    }

    @Test
    fun taskParserRejectsBlankResultText() {
        val json = validTaskJson.replace("\"resultText\": \"Полка выглядит спокойнее.\"", "\"resultText\": \"   \"")

        val failure = runCatching { parseTaskCatalog(json) }.exceptionOrNull()

        assertTrue(failure is IllegalArgumentException)
        assertEquals("Задача home_001 должна содержать результат.", failure?.message)
    }
}
