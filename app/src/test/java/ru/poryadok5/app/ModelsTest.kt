package ru.poryadok5.app

import ru.poryadok5.app.domain.EnergyLevel
import ru.poryadok5.app.domain.SupportedTaskMinutes
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.isRouteSafeTaskId
import ru.poryadok5.app.domain.normalizedTaskMinutes
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ModelsTest {
    @Test
    fun taskAreaFromRawTrimsAndIgnoresCase() {
        assertEquals(TaskArea.Digital, TaskArea.fromRaw(" digital "))
        assertEquals(TaskArea.Work, TaskArea.fromRaw(" WORK "))
    }

    @Test
    fun taskAreaFromRawFallsBackToHomeForUnknownValues() {
        assertEquals(TaskArea.Home, TaskArea.fromRaw("ArchivedArea"))
        assertEquals(TaskArea.Home, TaskArea.fromRaw("   "))
    }

    @Test
    fun energyLevelFromRawTrimsAndIgnoresCase() {
        assertEquals(EnergyLevel.Medium, EnergyLevel.fromRaw(" medium "))
        assertEquals(EnergyLevel.Active, EnergyLevel.fromRaw(" ACTIVE "))
    }

    @Test
    fun energyLevelFromRawFallsBackToLightForUnknownValues() {
        assertEquals(EnergyLevel.Light, EnergyLevel.fromRaw("ArchivedEnergy"))
        assertEquals(EnergyLevel.Light, EnergyLevel.fromRaw("   "))
    }

    @Test
    fun taskMinutesNormalizeToAllowedValues() {
        assertEquals(setOf(3, 5, 10), SupportedTaskMinutes)
        assertEquals(3, normalizedTaskMinutes(3))
        assertEquals(5, normalizedTaskMinutes(5))
        assertEquals(10, normalizedTaskMinutes(10))
        assertEquals(5, normalizedTaskMinutes(0))
        assertEquals(5, normalizedTaskMinutes(7))
        assertEquals(5, normalizedTaskMinutes(-1))
    }

    @Test
    fun taskIdsValidateRouteSafeCatalogShape() {
        assertTrue(isRouteSafeTaskId("home_001"))
        assertTrue(isRouteSafeTaskId("work_016"))
        assertTrue(isRouteSafeTaskId("digital_010"))
        assertFalse(isRouteSafeTaskId("home:001"))
        assertFalse(isRouteSafeTaskId(" home_001 "))
        assertFalse(isRouteSafeTaskId("home_1"))
        assertFalse(isRouteSafeTaskId("other_001"))
    }
}
