package ru.poryadok5.app.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.animateFloatAsState
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.Saver
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.onClick
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import ru.poryadok5.app.BuildConfig
import ru.poryadok5.app.data.UserPreferencesRepository
import ru.poryadok5.app.domain.AppPreferences
import ru.poryadok5.app.domain.CountdownTimerRules
import ru.poryadok5.app.domain.EnergyLevel
import ru.poryadok5.app.domain.MicroTask
import ru.poryadok5.app.domain.PoryadokEngine
import ru.poryadok5.app.domain.SupportedTaskMinutes
import ru.poryadok5.app.domain.TaskArea
import ru.poryadok5.app.domain.TaskFilter
import ru.poryadok5.app.domain.TaskSuggestionQuality
import ru.poryadok5.app.domain.isRouteSafeTaskId
import ru.poryadok5.app.domain.normalizedTaskMinutes
import ru.poryadok5.app.ui.components.AppCard
import ru.poryadok5.app.ui.components.ChoiceChip
import ru.poryadok5.app.ui.components.DangerAction
import ru.poryadok5.app.ui.components.MetricPill
import ru.poryadok5.app.ui.components.MetricTone
import ru.poryadok5.app.ui.components.PrimaryAction
import ru.poryadok5.app.ui.components.ProgressLine
import ru.poryadok5.app.ui.components.SecondaryAction
import ru.poryadok5.app.ui.components.StepRow
import ru.poryadok5.app.ui.components.TopBar
import ru.poryadok5.app.ui.theme.BlueSoft
import ru.poryadok5.app.ui.theme.Cream
import ru.poryadok5.app.ui.theme.MutedText
import ru.poryadok5.app.ui.theme.Sage
import ru.poryadok5.app.ui.theme.SageSoft
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.Locale

private sealed interface AppScreen {
    data object Onboarding : AppScreen
    data object Home : AppScreen
    data object Progress : AppScreen
    data object Settings : AppScreen
    data class Details(val taskId: String) : AppScreen
    data class Timer(val taskId: String) : AppScreen
    data class Result(val taskId: String) : AppScreen
}

private val AppScreenSaver = Saver<AppScreen, String>(
    save = { screen -> screen.toRoute() },
    restore = { route -> appScreenFromRoute(route) },
)

private val RussianLocale = Locale("ru")
private val ContentMaxWidth = 720.dp
private val StatsIcon: ImageVector = ImageVector.Builder(
    name = "StatsBars",
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
).apply {
    path(fill = SolidColor(Color.Black)) {
        moveTo(4f, 12f)
        horizontalLineTo(8f)
        verticalLineTo(20f)
        horizontalLineTo(4f)
        close()
        moveTo(10f, 7f)
        horizontalLineTo(14f)
        verticalLineTo(20f)
        horizontalLineTo(10f)
        close()
        moveTo(16f, 4f)
        horizontalLineTo(20f)
        verticalLineTo(20f)
        horizontalLineTo(16f)
        close()
    }
}.build()

private val HomeIcon: ImageVector = ImageVector.Builder(
    name = "Home",
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
).apply {
    path(fill = SolidColor(Color.Black)) {
        moveTo(4f, 11f)
        lineTo(12f, 4f)
        lineTo(20f, 11f)
        lineTo(18.7f, 12.5f)
        lineTo(17.5f, 11.5f)
        verticalLineTo(19f)
        horizontalLineTo(13.5f)
        verticalLineTo(14.5f)
        horizontalLineTo(10.5f)
        verticalLineTo(19f)
        horizontalLineTo(6.5f)
        verticalLineTo(11.5f)
        lineTo(5.3f, 12.5f)
        close()
    }
}.build()

private val PauseIcon: ImageVector = ImageVector.Builder(
    name = "Pause",
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
).apply {
    path(fill = SolidColor(Color.Black)) {
        moveTo(6f, 5f)
        horizontalLineTo(10f)
        verticalLineTo(19f)
        horizontalLineTo(6f)
        close()
        moveTo(14f, 5f)
        horizontalLineTo(18f)
        verticalLineTo(19f)
        horizontalLineTo(14f)
        close()
    }
}.build()

private val ChevronDownIcon: ImageVector = ImageVector.Builder(
    name = "ChevronDown",
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
).apply {
    path(fill = SolidColor(Color.Black)) {
        moveTo(7.4f, 8.6f)
        lineTo(12f, 13.2f)
        lineTo(16.6f, 8.6f)
        lineTo(18f, 10f)
        lineTo(12f, 16f)
        lineTo(6f, 10f)
        close()
    }
}.build()

private val ChevronUpIcon: ImageVector = ImageVector.Builder(
    name = "ChevronUp",
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
).apply {
    path(fill = SolidColor(Color.Black)) {
        moveTo(7.4f, 15.4f)
        lineTo(12f, 10.8f)
        lineTo(16.6f, 15.4f)
        lineTo(18f, 14f)
        lineTo(12f, 8f)
        lineTo(6f, 14f)
        close()
    }
}.build()

@Composable
fun PoryadokApp(
    tasks: List<MicroTask>,
    preferences: AppPreferences,
    preferencesRepository: UserPreferencesRepository,
) {
    val engine = remember(tasks) { PoryadokEngine(tasks) }
    val scope = rememberCoroutineScope()
    val haptic = LocalHapticFeedback.current

    var screen by rememberSaveable(stateSaver = AppScreenSaver) {
        mutableStateOf<AppScreen>(
            if (preferences.settings.onboardingDone) AppScreen.Home else AppScreen.Onboarding,
        )
    }
    var selectedAreaName by rememberSaveable { mutableStateOf(preferences.settings.preferredArea.name) }
    var selectedEnergyName by rememberSaveable { mutableStateOf(EnergyLevel.Light.name) }
    var selectedMinutes by rememberSaveable { mutableIntStateOf(5) }
    var skippedSuggestionIds by rememberSaveable { mutableStateOf(emptyList<String>()) }

    LaunchedEffect(preferences.settings.onboardingDone) {
        if (!preferences.settings.onboardingDone) {
            screen = AppScreen.Onboarding
        } else if (screen is AppScreen.Onboarding) {
            selectedAreaName = preferences.settings.preferredArea.name
            screen = AppScreen.Home
        }
    }

    val selectedArea = TaskArea.fromRaw(selectedAreaName)
    val selectedEnergy = EnergyLevel.fromRaw(selectedEnergyName)
    val selectedDuration = normalizedTaskMinutes(selectedMinutes)
    val filter = TaskFilter(selectedArea, selectedEnergy, selectedDuration)
    val skippedSuggestionIdSet = skippedSuggestionIds.toSet()
    val suggested = engine.suggestTask(
        filter = filter,
        completedIds = preferences.progress.completedTaskIds,
        excludedIds = skippedSuggestionIdSet,
    )
    val canSkipSuggested = engine.hasAlternativeSuggestion(
        filter = filter,
        completedIds = preferences.progress.completedTaskIds,
        excludedIds = skippedSuggestionIdSet,
        currentTaskId = suggested.id,
    )

    LaunchedEffect(selectedAreaName, selectedEnergyName, selectedMinutes, preferences.progress.completedTaskIds) {
        skippedSuggestionIds = emptyList()
    }

    BackHandler(enabled = screen !is AppScreen.Home && screen !is AppScreen.Onboarding) {
        screen = when (val current = screen) {
            is AppScreen.Details -> AppScreen.Home
            AppScreen.Progress -> AppScreen.Home
            AppScreen.Settings -> AppScreen.Home
            is AppScreen.Timer -> AppScreen.Details(current.taskId)
            is AppScreen.Result -> AppScreen.Home
            AppScreen.Home, AppScreen.Onboarding -> screen
        }
    }

    Scaffold(
        modifier = Modifier
            .fillMaxSize()
            .safeDrawingPadding()
            .navigationBarsPadding(),
        containerColor = Cream,
    ) { padding ->
        Box(modifier = Modifier.padding(padding)) {
            when (val current = screen) {
                AppScreen.Onboarding -> OnboardingScreen(
                    selectedArea = selectedArea,
                    onAreaSelected = { selectedAreaName = it.name },
                    onContinue = {
                        scope.launch {
                            preferencesRepository.completeOnboarding(selectedArea)
                            screen = AppScreen.Home
                        }
                    },
                )

                AppScreen.Home -> HomeScreen(
                    preferences = preferences,
                    engine = engine,
                    filter = filter,
                    suggested = suggested,
                    onAreaSelected = { selectedAreaName = it.name },
                    onEnergySelected = { selectedEnergyName = it.name },
                    onMinutesSelected = { selectedMinutes = it },
                    onOpenTask = { screen = AppScreen.Details(suggested.id) },
                    onStartTask = { screen = AppScreen.Timer(suggested.id) },
                    canSkipTask = canSkipSuggested,
                    onSkipTask = {
                        skippedSuggestionIds = (skippedSuggestionIds + suggested.id)
                            .distinct()
                            .takeLast(engine.totalTasks().coerceAtLeast(1))
                    },
                    onProgress = { screen = AppScreen.Progress },
                    onSettings = { screen = AppScreen.Settings },
                )

                AppScreen.Progress -> ProgressScreen(
                    preferences = preferences,
                    engine = engine,
                    onBack = { screen = AppScreen.Home },
                    onHome = { screen = AppScreen.Home },
                    onSettings = { screen = AppScreen.Settings },
                )

                AppScreen.Settings -> SettingsScreen(
                    preferences = preferences,
                    catalogSize = engine.totalTasks(),
                    onBack = { screen = AppScreen.Home },
                    onPreferredArea = {
                        scope.launch {
                            preferencesRepository.setPreferredArea(it)
                            selectedAreaName = it.name
                        }
                    },
                    onHaptics = { enabled ->
                        scope.launch { preferencesRepository.setHapticsEnabled(enabled) }
                    },
                    onResetProgress = {
                        scope.launch { preferencesRepository.resetProgress() }
                    },
                )

                is AppScreen.Details -> {
                    val task = tasks.firstOrNull { it.id == current.taskId } ?: suggested
                    TaskDetailsScreen(
                        task = task,
                        onBack = { screen = AppScreen.Home },
                        onStart = { screen = AppScreen.Timer(task.id) },
                    )
                }

                is AppScreen.Timer -> {
                    val task = tasks.firstOrNull { it.id == current.taskId } ?: suggested
                    TimerScreen(
                        task = task,
                        onBack = { screen = AppScreen.Details(task.id) },
                        onComplete = {
                            if (preferences.settings.hapticsEnabled) {
                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            }
                            scope.launch {
                                preferencesRepository.recordCompletion(task.id)
                                screen = AppScreen.Result(task.id)
                            }
                        },
                    )
                }

                is AppScreen.Result -> {
                    val task = tasks.firstOrNull { it.id == current.taskId } ?: suggested
                    val nextTask = engine.suggestAfterCompletion(
                        filter = filter,
                        completedIds = preferences.progress.completedTaskIds,
                        completedTaskId = task.id,
                    )
                    val hasFreshNextTask = engine.hasUncompletedTasksAfterCompletion(
                        completedIds = preferences.progress.completedTaskIds,
                        completedTaskId = task.id,
                    )
                    ResultScreen(
                        task = task,
                        nextTask = nextTask,
                        hasFreshNextTask = hasFreshNextTask,
                        preferences = preferences,
                        progressPercent = engine.progressPercent(preferences.progress.completedTaskIds),
                        onHome = { screen = AppScreen.Home },
                        onNext = { screen = AppScreen.Timer(nextTask.id) },
                        onOpenNext = { screen = AppScreen.Details(nextTask.id) },
                        onProgress = { screen = AppScreen.Progress },
                    )
                }
            }
        }
    }
}

@Composable
private fun OnboardingScreen(
    selectedArea: TaskArea,
    onAreaSelected: (TaskArea) -> Unit,
    onContinue: () -> Unit,
) {
    ScreenColumn {
        Spacer(Modifier.height(8.dp))
        Text(
            text = "Порядок 5",
            style = MaterialTheme.typography.displaySmall,
        )
        Text(
            text = "Короткие задачи на 3, 5 и 10 минут, чтобы вернуть порядок без большой уборки.",
            style = MaterialTheme.typography.bodyLarge,
            color = MutedText,
        )
        AppCard(containerColor = SageSoft) {
            Text("С чего начнём?", style = MaterialTheme.typography.titleLarge)
            Text(
                "Выберите зону, которая чаще всего мешает спокойному дню. Настройку можно изменить позже.",
                style = MaterialTheme.typography.bodyMedium,
            )
            AreaSelector(selectedArea, onAreaSelected)
        }
        OnboardingFlowSummary()
        PrimaryAction(
            text = "Начать",
            onClick = onContinue,
            icon = Icons.Filled.PlayArrow,
        )
    }
}

@Composable
private fun OnboardingFlowSummary() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 4.dp, vertical = 2.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text("Первые 5 минут", style = MaterialTheme.typography.titleMedium)
        OnboardingFlowFact("Сначала", "Выбираете стартовую зону.")
        OnboardingFlowFact("Затем", "Получаете задачу и при желании уточняете подбор.")
        OnboardingFlowFact("После", "Запускаете таймер и отмечаете результат.")
    }
}

@Composable
private fun OnboardingFlowFact(label: String, text: String) {
    Row(
        modifier = Modifier.defaultMinSize(minHeight = 48.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .background(Sage, CircleShape),
        )
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = MaterialTheme.typography.titleMedium, color = Sage)
            Text(text, style = MaterialTheme.typography.bodyMedium, color = MutedText)
        }
    }
}

@Composable
private fun HomeScreen(
    preferences: AppPreferences,
    engine: PoryadokEngine,
    filter: TaskFilter,
    suggested: MicroTask,
    onAreaSelected: (TaskArea) -> Unit,
    onEnergySelected: (EnergyLevel) -> Unit,
    onMinutesSelected: (Int) -> Unit,
    onOpenTask: () -> Unit,
    onStartTask: () -> Unit,
    canSkipTask: Boolean,
    onSkipTask: () -> Unit,
    onProgress: () -> Unit,
    onSettings: () -> Unit,
) {
    var filtersExpanded by rememberSaveable { mutableStateOf(false) }

    ScreenColumn {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("Порядок 5", style = MaterialTheme.typography.headlineMedium)
                Text("Одна маленькая задача прямо сейчас.", style = MaterialTheme.typography.bodyMedium)
            }
            HeaderAction(label = "Итоги", icon = StatsIcon, onAction = onProgress)
            Spacer(Modifier.width(8.dp))
            HeaderAction(label = "Опции", icon = Icons.Filled.Settings, onAction = onSettings)
        }

        TaskCard(
            task = suggested,
            completed = suggested.id in preferences.progress.completedTaskIds,
            label = "Задача на сейчас",
            selectionNote = engine.suggestionQuality(filter, suggested).homeSelectionNote(),
            showResult = true,
        )
        PrimaryAction(
            text = "Запустить таймер",
            onClick = onStartTask,
            icon = Icons.Filled.PlayArrow,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryAction(
                text = "Другая задача",
                onClick = onSkipTask,
                enabled = canSkipTask,
                modifier = Modifier.weight(1f),
                icon = Icons.Filled.Refresh,
            )
            SecondaryAction(
                text = "Все шаги",
                onClick = onOpenTask,
                modifier = Modifier.weight(1f),
                icon = Icons.AutoMirrored.Filled.List,
            )
        }
        AnimatedVisibility(visible = !canSkipTask) {
            Text(
                text = "Других задач по этому подбору сейчас нет. Измените подбор или выполните текущую.",
                style = MaterialTheme.typography.bodyMedium,
                color = MutedText,
            )
        }

        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            MetricPill("выполнено", preferences.progress.totalDone.toString(), MetricTone.Sage, Modifier.weight(1f))
            MetricPill("серия", "${preferences.progress.streakDays} дн.", MetricTone.Amber, Modifier.weight(1f))
            MetricPill("каталог", "${engine.progressPercent(preferences.progress.completedTaskIds)}%", MetricTone.Blue, Modifier.weight(1f))
        }

        HomeFilterDisclosure(
            filter = filter,
            expanded = filtersExpanded,
            onToggle = { filtersExpanded = !filtersExpanded },
            onAreaSelected = onAreaSelected,
            onEnergySelected = onEnergySelected,
            onMinutesSelected = onMinutesSelected,
        )
    }
}

@Composable
private fun HomeFilterDisclosure(
    filter: TaskFilter,
    expanded: Boolean,
    onToggle: () -> Unit,
    onAreaSelected: (TaskArea) -> Unit,
    onEnergySelected: (EnergyLevel) -> Unit,
    onMinutesSelected: (Int) -> Unit,
) {
    if (expanded) {
        AppCard {
            HomeFilterSummaryRow(filter = filter, expanded = true, onToggle = onToggle)
            AnimatedVisibility(visible = expanded) {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
                    Text("Зона", style = MaterialTheme.typography.titleMedium)
                    AreaSelector(filter.area, onAreaSelected)
                    HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
                    Text("Энергия", style = MaterialTheme.typography.titleMedium)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        EnergyLevel.entries.forEach { energy ->
                            ChoiceChip(
                                text = energy.label,
                                selected = filter.energy == energy,
                                onClick = { onEnergySelected(energy) },
                                modifier = Modifier.weight(1f),
                            )
                        }
                    }
                    HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
                    Text("Время", style = MaterialTheme.typography.titleMedium)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        SupportedTaskMinutes.forEach { minutes ->
                            ChoiceChip(
                                text = "$minutes мин",
                                selected = filter.minutes == minutes,
                                onClick = { onMinutesSelected(minutes) },
                                modifier = Modifier.weight(1f),
                            )
                        }
                    }
                }
            }
        }
    } else {
        Column(modifier = Modifier.fillMaxWidth()) {
            HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
            HomeFilterSummaryRow(
                filter = filter,
                expanded = false,
                onToggle = onToggle,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp),
            )
            HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
        }
    }
}

@Composable
private fun HomeFilterSummaryRow(
    filter: TaskFilter,
    expanded: Boolean,
    onToggle: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .clickable(
                role = Role.Button,
                onClick = onToggle,
            )
            .semantics {
                stateDescription = if (expanded) "Подбор раскрыт" else "Подбор скрыт"
            }
            .padding(horizontal = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text("Настроить подбор", style = MaterialTheme.typography.titleMedium)
            Text(
                "${filter.area.label} · ${filter.energy.label.lowercase(RussianLocale)} · ${filter.minutes} мин",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        FilterDisclosureIndicator(expanded = expanded)
    }
}

@Composable
private fun FilterDisclosureIndicator(expanded: Boolean) {
    Row(
        modifier = Modifier
            .defaultMinSize(minHeight = 48.dp)
            .padding(start = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = if (expanded) "Скрыть" else "Изменить",
            style = MaterialTheme.typography.titleMedium,
            color = Sage,
        )
        Icon(
            imageVector = if (expanded) ChevronUpIcon else ChevronDownIcon,
            contentDescription = null,
            tint = Sage,
            modifier = Modifier.size(22.dp),
        )
    }
}

@Composable
private fun TaskDetailsScreen(
    task: MicroTask,
    onBack: () -> Unit,
    onStart: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize()) {
        TopBar(title = "Задача", onBack = onBack)
        Box(modifier = Modifier.weight(1f)) {
            ScreenColumn(includeTopPadding = false) {
                TaskCard(
                    task = task,
                    completed = false,
                    label = "Выбранная задача",
                    showFirstStep = false,
                    statusText = "выбрана",
                )
                AppCard(containerColor = SageSoft) {
                    Text("Перед стартом", style = MaterialTheme.typography.titleMedium)
                    Text(
                        "Выполните шаги сверху вниз. Достаточно заметного улучшения, не идеального порядка.",
                        style = MaterialTheme.typography.bodyLarge,
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        DetailBriefingFact(
                            label = "зона",
                            value = task.area.label,
                            modifier = Modifier.weight(1f),
                        )
                        DetailBriefingFact(
                            label = "энергия",
                            value = task.energy.label,
                            modifier = Modifier.weight(1f),
                        )
                        DetailBriefingFact(
                            label = "время",
                            value = "${task.minutes} мин",
                            modifier = Modifier.weight(1f),
                        )
                    }
                    TaskResultPreview(task.resultText)
                }
                AppCard {
                    Text("Шаги", style = MaterialTheme.typography.titleLarge)
                    task.steps.forEachIndexed { index, step ->
                        StepRow(index + 1, step)
                    }
                }
                Spacer(Modifier.height(88.dp))
            }
            BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter)) {
                PrimaryAction(
                    text = "Начать ${task.minutes} мин",
                    onClick = onStart,
                    icon = Icons.Filled.PlayArrow,
                )
            }
        }
    }
}

@Composable
private fun DetailBriefingFact(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MutedText,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
        )
        Text(
            text = value,
            style = MaterialTheme.typography.labelLarge,
            color = Sage,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun TimerScreen(
    task: MicroTask,
    onBack: () -> Unit,
    onComplete: () -> Unit,
) {
    val totalSeconds = task.minutes * 60
    var remainingSeconds by rememberSaveable(task.id) { mutableIntStateOf(totalSeconds) }
    var running by rememberSaveable(task.id) { mutableStateOf(true) }
    var endAtMillis by rememberSaveable(task.id) {
        mutableLongStateOf(CountdownTimerRules.endAtMillis(System.currentTimeMillis(), totalSeconds))
    }
    var completionSubmitted by rememberSaveable(task.id) { mutableStateOf(false) }
    val timerExpired = remainingSeconds == 0
    val progress by animateFloatAsState(
        targetValue = 1f - (remainingSeconds.toFloat() / totalSeconds.toFloat()),
        label = "timerProgress",
    )

    LaunchedEffect(task.id, running, endAtMillis) {
        while (running) {
            val nextRemaining = CountdownTimerRules.remainingSeconds(endAtMillis, System.currentTimeMillis())
            remainingSeconds = nextRemaining
            if (nextRemaining == 0) {
                running = false
                break
            }
            delay(250)
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        TopBar(title = "Таймер", onBack = onBack)
        Box(modifier = Modifier.weight(1f)) {
            ScreenColumn(includeTopPadding = false) {
                AppCard(containerColor = SageSoft) {
                    Text(task.title, style = MaterialTheme.typography.titleLarge)
                    Text("${task.area.label} · ${task.energy.label}", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "Цель: ${task.minutes} мин",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    ProgressLine(
                        progress = progress,
                        modifier = Modifier
                            .fillMaxWidth(),
                        trackColor = MaterialTheme.colorScheme.surface,
                    )
                    Text(
                        text = formatTime(remainingSeconds),
                        modifier = Modifier.fillMaxWidth(),
                        textAlign = TextAlign.Center,
                        style = MaterialTheme.typography.displaySmall,
                    )
                    Text(
                        text = if (timerExpired) "Время вышло. Отметьте результат или завершите позже." else "Двигайтесь спокойно, без идеальной уборки.",
                        style = MaterialTheme.typography.bodyMedium,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
                AppCard {
                    Text("План", style = MaterialTheme.typography.titleMedium)
                    task.steps.forEachIndexed { index, step -> StepRow(index + 1, step) }
                    TaskResultPreview(task.resultText)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    SecondaryAction(
                        text = when {
                            timerExpired -> "Время вышло"
                            running -> "Пауза"
                            else -> "Продолжить"
                        },
                        onClick = {
                            val now = System.currentTimeMillis()
                            if (running) {
                                remainingSeconds = CountdownTimerRules.remainingSeconds(endAtMillis, now)
                                running = false
                            } else if (remainingSeconds > 0) {
                                endAtMillis = CountdownTimerRules.endAtMillis(now, remainingSeconds)
                                running = true
                            }
                        },
                        enabled = !timerExpired,
                        icon = if (running) PauseIcon else Icons.Filled.PlayArrow,
                        modifier = Modifier.weight(1f),
                    )
                    SecondaryAction(
                        text = "Сброс",
                        onClick = {
                            remainingSeconds = totalSeconds
                            endAtMillis = CountdownTimerRules.endAtMillis(System.currentTimeMillis(), totalSeconds)
                            running = true
                        },
                        icon = Icons.Filled.Refresh,
                        modifier = Modifier.weight(1f),
                    )
                }
                Spacer(Modifier.height(88.dp))
            }
            BottomActionDock(modifier = Modifier.align(Alignment.BottomCenter)) {
                PrimaryAction(
                    text = "Готово",
                    onClick = {
                        if (!completionSubmitted) {
                            completionSubmitted = true
                            running = false
                            onComplete()
                        }
                    },
                    enabled = !completionSubmitted,
                    icon = Icons.Filled.Done,
                )
            }
        }
    }
}

@Composable
private fun BottomActionDock(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        color = Cream,
        shadowElevation = 4.dp,
    ) {
        Box(
            modifier = Modifier.fillMaxWidth(),
            contentAlignment = Alignment.TopCenter,
        ) {
            Column(
                modifier = Modifier
                    .widthIn(max = ContentMaxWidth)
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                content = content,
            )
        }
    }
}

@Composable
private fun ResultScreen(
    task: MicroTask,
    nextTask: MicroTask,
    hasFreshNextTask: Boolean,
    preferences: AppPreferences,
    progressPercent: Int,
    onHome: () -> Unit,
    onNext: () -> Unit,
    onOpenNext: () -> Unit,
    onProgress: () -> Unit,
) {
    ScreenColumn {
        Text("Готово", style = MaterialTheme.typography.displaySmall)
        Text("Сделано: ${task.title}", style = MaterialTheme.typography.titleMedium, color = Sage)
        Text(task.resultText, style = MaterialTheme.typography.bodyLarge, color = MutedText)
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            MetricPill("выполнено", preferences.progress.totalDone.toString(), MetricTone.Sage, Modifier.weight(1f))
            MetricPill("серия", "${preferences.progress.streakDays} дн.", MetricTone.Amber, Modifier.weight(1f))
            MetricPill("каталог", "$progressPercent%", MetricTone.Blue, Modifier.weight(1f))
        }
        TaskCard(
            task = nextTask,
            completed = !hasFreshNextTask,
            label = if (hasFreshNextTask) "Дальше без повтора" else "Каталог пройден",
            showResult = true,
            statusText = if (hasFreshNextTask) "новая" else "повтор",
        )
        if (!hasFreshNextTask) {
            AppCard(containerColor = BlueSoft) {
                Text("Все задачи отмечены", style = MaterialTheme.typography.titleMedium)
                Text("Можно повторить любую задачу или сбросить прогресс в настройках, если хотите начать каталог заново.", style = MaterialTheme.typography.bodyLarge)
            }
        }
        if (hasFreshNextTask) {
            PrimaryAction(
                text = "Посмотреть следующую",
                onClick = onOpenNext,
                icon = Icons.AutoMirrored.Filled.List,
            )
            SecondaryAction(
                text = "Запустить таймер",
                onClick = onNext,
                icon = Icons.Filled.PlayArrow,
            )
        } else {
            PrimaryAction(
                text = "Повторить задачу",
                onClick = onNext,
                icon = Icons.Filled.Refresh,
            )
            SecondaryAction(
                text = "Посмотреть шаги",
                onClick = onOpenNext,
                icon = Icons.AutoMirrored.Filled.List,
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryAction(
                text = "На главный экран",
                onClick = onHome,
                icon = HomeIcon,
                modifier = Modifier.weight(1f),
            )
            SecondaryAction(
                text = "Посмотреть итоги",
                onClick = onProgress,
                icon = StatsIcon,
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun ProgressScreen(
    preferences: AppPreferences,
    engine: PoryadokEngine,
    onBack: () -> Unit,
    onHome: () -> Unit,
    onSettings: () -> Unit,
) {
    val completedCatalogCount = engine.completedCount(preferences.progress.completedTaskIds)
    val totalCatalogCount = engine.totalTasks()
    val catalogPercent = engine.progressPercent(preferences.progress.completedTaskIds)
    val nextFocusArea = engine.nextFocusArea(preferences.progress.completedTaskIds)

    Column(modifier = Modifier.fillMaxSize()) {
        TopBar(
            title = "Итоги",
            onBack = onBack,
            action = { HeaderAction(label = "Опции", icon = Icons.Filled.Settings, onAction = onSettings) },
        )
        ScreenColumn(includeTopPadding = false) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                MetricPill("выполнено", preferences.progress.totalDone.toString(), MetricTone.Sage, Modifier.weight(1f))
                MetricPill("серия", "${preferences.progress.streakDays} дн.", MetricTone.Amber, Modifier.weight(1f))
                MetricPill("каталог", "$catalogPercent%", MetricTone.Blue, Modifier.weight(1f))
            }
            AppCard {
                Text("Каталог", style = MaterialTheme.typography.titleLarge)
                Text(
                    "Отмечено задач: $completedCatalogCount из $totalCatalogCount.",
                    style = MaterialTheme.typography.bodyLarge,
                )
                ProgressLine(progress = catalogPercent / 100f)
                HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
                ProgressFocusSummary(
                    area = nextFocusArea,
                    completed = nextFocusArea?.let { engine.completedCountByArea(it, preferences.progress.completedTaskIds) } ?: completedCatalogCount,
                    total = nextFocusArea?.let(engine::countByArea) ?: totalCatalogCount,
                )
            }
            AppCard {
                Text("Зоны", style = MaterialTheme.typography.titleLarge)
                TaskArea.entries.forEach { area ->
                    AreaProgressRow(
                        area = area,
                        completed = engine.completedCountByArea(area, preferences.progress.completedTaskIds),
                        total = engine.countByArea(area),
                    )
                }
            }
            AppCard(containerColor = BlueSoft) {
                Text("Ритм", style = MaterialTheme.typography.titleMedium)
                ProgressRhythmSummary()
            }
            PrimaryAction(
                text = "Продолжить с задачей",
                onClick = onHome,
                icon = Icons.AutoMirrored.Filled.ArrowForward,
            )
        }
    }
}

@Composable
private fun SettingsScreen(
    preferences: AppPreferences,
    catalogSize: Int,
    onBack: () -> Unit,
    onPreferredArea: (TaskArea) -> Unit,
    onHaptics: (Boolean) -> Unit,
    onResetProgress: () -> Unit,
) {
    var confirmReset by rememberSaveable { mutableStateOf(false) }
    var resetNoticeVisible by rememberSaveable { mutableStateOf(false) }
    Column(modifier = Modifier.fillMaxSize()) {
        TopBar(title = "Настройки", onBack = onBack)
        ScreenColumn(includeTopPadding = false) {
            AppCard {
                Text("Зона по умолчанию", style = MaterialTheme.typography.titleLarge)
                AreaSelector(preferences.settings.preferredArea, onPreferredArea)
            }
            AppCard {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .defaultMinSize(minHeight = 56.dp)
                        .toggleable(
                            value = preferences.settings.hapticsEnabled,
                            role = Role.Switch,
                            onValueChange = onHaptics,
                        ),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Тактильный отклик", style = MaterialTheme.typography.titleMedium)
                        Text("Короткий сигнал после завершения задачи.", style = MaterialTheme.typography.bodyMedium)
                    }
                    Switch(
                        checked = preferences.settings.hapticsEnabled,
                        onCheckedChange = null,
                    )
                }
            }
            AppCard(containerColor = SageSoft) {
                Text("Приватность", style = MaterialTheme.typography.titleLarge)
                Text(
                    "Прогресс хранится только на устройстве. Ничего не отправляем.",
                    style = MaterialTheme.typography.bodyLarge,
                )
                PrivacyBadgeGrid()
            }
            AppCard(containerColor = BlueSoft) {
                Text("О приложении", style = MaterialTheme.typography.titleLarge)
                Text("Порядок 5", style = MaterialTheme.typography.titleMedium)
                SettingsAboutSummary(catalogSize = catalogSize)
            }
            Spacer(modifier = Modifier.height(32.dp))
            AppCard {
                Text("Сброс прогресса", style = MaterialTheme.typography.titleMedium)
                Text("Список задач останется, но счётчик, серия и выполненные отметки очистятся.", style = MaterialTheme.typography.bodyMedium)
                AnimatedVisibility(visible = confirmReset) {
                    Text("Подтвердите сброс ещё одним нажатием.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.error)
                }
                AnimatedVisibility(visible = resetNoticeVisible) {
                    Text("Готово. Прогресс сброшен, можно начать заново.", style = MaterialTheme.typography.bodyMedium, color = Sage)
                }
                if (confirmReset) {
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        SecondaryAction(
                            text = "Отмена",
                            onClick = {
                                confirmReset = false
                                resetNoticeVisible = false
                            },
                            modifier = Modifier.weight(1f),
                        )
                        DangerAction(
                            text = "Сбросить прогресс",
                            onClick = {
                                onResetProgress()
                                confirmReset = false
                                resetNoticeVisible = true
                            },
                            modifier = Modifier.weight(1f),
                        )
                    }
                } else {
                    SecondaryAction(
                        text = "Подготовить сброс",
                        onClick = {
                            resetNoticeVisible = false
                            confirmReset = true
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun SettingsAboutSummary(catalogSize: Int) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        SettingsAboutFact(
            label = "Версия",
            value = BuildConfig.VERSION_NAME,
            modifier = Modifier.weight(0.85f),
        )
        SettingsAboutFact(
            label = "Каталог",
            value = "$catalogSize задач",
            modifier = Modifier.weight(1f),
        )
        SettingsAboutFact(
            label = "Данные",
            value = "на устройстве",
            modifier = Modifier.weight(1.35f),
        )
    }
}

@Composable
private fun SettingsAboutFact(label: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MutedText)
        Text(value, style = MaterialTheme.typography.labelLarge, color = Sage)
    }
}

@Composable
private fun PrivacyBadgeGrid() {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            PrivacyBadge("Без интернета", "работает офлайн", Modifier.weight(1f))
            PrivacyBadge("Без аккаунта", "вход не нужен", Modifier.weight(1f))
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            PrivacyBadge("Без рекламы", "нет баннеров", Modifier.weight(1f))
            PrivacyBadge("Без аналитики", "нет трекеров", Modifier.weight(1f))
        }
    }
}

@Composable
private fun ProgressFocusSummary(area: TaskArea?, completed: Int, total: Int) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .padding(top = 8.dp)
                .size(8.dp)
                .background(if (area == null) Sage else MaterialTheme.colorScheme.secondary, CircleShape),
        )
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(
                text = if (area == null) "Каталог закрыт" else "Следующая зона",
                style = MaterialTheme.typography.labelLarge,
                color = Sage,
            )
            Text(
                text = if (area == null) {
                    "Все $total задач отмечены. Можно повторять любимые задачи или начать каталог заново."
                } else {
                    "${area.label}: $completed из $total. Хорошая точка для следующей 5-минутки."
                },
                style = MaterialTheme.typography.bodyMedium,
                color = MutedText,
            )
        }
    }
}

@Composable
private fun ProgressRhythmSummary() {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ProgressRhythmItem(
            label = "Серия",
            value = "1 раз в день",
            modifier = Modifier.weight(1f),
        )
        ProgressRhythmItem(
            label = "Счётчик",
            value = "каждая задача",
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun ProgressRhythmItem(label: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(label, style = MaterialTheme.typography.labelLarge, color = Sage)
        Text(value, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun PrivacyBadge(label: String, detail: String, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier
            .defaultMinSize(minHeight = 56.dp)
            .padding(horizontal = 4.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .padding(top = 8.dp)
                .size(7.dp)
                .background(Sage, CircleShape),
        )
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label, style = MaterialTheme.typography.labelLarge)
            Text(detail, style = MaterialTheme.typography.bodySmall, color = MutedText)
        }
    }
}

@Composable
private fun TaskCard(
    task: MicroTask,
    completed: Boolean,
    label: String? = null,
    selectionNote: String? = null,
    showFirstStep: Boolean = true,
    showResult: Boolean = false,
    statusText: String? = null,
) {
    AppCard(
        modifier = Modifier.animateContentSize(),
        containerColor = if (completed) SageSoft else MaterialTheme.colorScheme.surface,
    ) {
        if (label != null) {
            Text(label, style = MaterialTheme.typography.labelLarge, color = Sage)
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(task.title, style = MaterialTheme.typography.titleLarge)
                Text(
                    "${task.area.label} · ${task.energy.label.lowercase(RussianLocale)} · ${task.minutes} мин",
                    style = MaterialTheme.typography.bodyMedium,
                )
                if (selectionNote != null) {
                    Text(selectionNote, style = MaterialTheme.typography.bodyMedium, color = MutedText)
                }
            }
            TaskStatusPill(
                text = statusText ?: if (completed) "выполнено" else "новая",
                completed = completed,
            )
        }
        if (showFirstStep) {
            Text("Первый шаг", style = MaterialTheme.typography.titleMedium)
            Text(task.steps.first(), style = MaterialTheme.typography.bodyLarge)
        }
        if (showResult) {
            TaskResultPreview(task.resultText)
        }
    }
}

@Composable
private fun TaskResultPreview(resultText: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 48.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text("После", style = MaterialTheme.typography.labelLarge, color = Sage)
        Text(resultText, style = MaterialTheme.typography.bodyMedium, color = MutedText)
    }
}

@Composable
private fun TaskStatusPill(
    text: String,
    completed: Boolean,
    modifier: Modifier = Modifier,
) {
    val tone = if (completed) Sage else MutedText
    val dotColor = if (completed) Sage else MaterialTheme.colorScheme.secondary
    Row(
        modifier = modifier
            .defaultMinSize(minHeight = 32.dp)
            .padding(start = 12.dp, top = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Surface(
            modifier = Modifier.size(8.dp),
            shape = CircleShape,
            color = dotColor,
        ) {}
        Text(
            text = text,
            style = MaterialTheme.typography.labelLarge,
            color = tone,
        )
    }
}

@Composable
private fun AreaProgressRow(area: TaskArea, completed: Int, total: Int) {
    val progress = if (total == 0) 0f else completed.toFloat() / total.toFloat()
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(area.label, style = MaterialTheme.typography.bodyLarge)
            Text("$completed из $total", style = MaterialTheme.typography.bodyMedium)
        }
        ProgressLine(progress = progress, height = 6.dp)
    }
}

@Composable
private fun AreaSelector(selectedArea: TaskArea, onAreaSelected: (TaskArea) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        TaskArea.entries.chunked(3).forEach { rowAreas ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                rowAreas.forEach { area ->
                    ChoiceChip(
                        text = area.shortLabel,
                        selected = selectedArea == area,
                        onClick = { onAreaSelected(area) },
                        modifier = Modifier.weight(1f),
                    )
                }
                repeat(3 - rowAreas.size) {
                    Spacer(Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun HeaderAction(label: String, icon: ImageVector, onAction: () -> Unit) {
    Surface(
        modifier = Modifier
            .defaultMinSize(minWidth = 48.dp, minHeight = 48.dp)
            .clickable(role = Role.Button, onClick = onAction)
            .clearAndSetSemantics {
                role = Role.Button
                contentDescription = label
                onClick(label) {
                    onAction()
                    true
                }
            },
        shape = MaterialTheme.shapes.small,
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant),
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.size(48.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

@Composable
private fun ScreenColumn(
    includeTopPadding: Boolean = true,
    content: @Composable ColumnScope.() -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        contentAlignment = Alignment.TopCenter,
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = ContentMaxWidth)
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(top = if (includeTopPadding) 22.dp else 0.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            content = content,
        )
    }
}

private fun formatTime(seconds: Int): String {
    val minutes = seconds / 60
    val rest = seconds % 60
    return "%d:%02d".format(Locale.ROOT, minutes, rest)
}

private fun TaskSuggestionQuality.homeSelectionNote(): String {
    return when (this) {
        TaskSuggestionQuality.Exact -> "Совпадает с выбором"
        TaskSuggestionQuality.AreaAndDuration -> "Зона и время совпали"
        TaskSuggestionQuality.CatalogFallback -> "Ближайшая свободная задача"
    }
}

private fun AppScreen.toRoute(): String {
    return when (this) {
        AppScreen.Onboarding -> "onboarding"
        AppScreen.Home -> "home"
        AppScreen.Progress -> "progress"
        AppScreen.Settings -> "settings"
        is AppScreen.Details -> "details:$taskId"
        is AppScreen.Timer -> "timer:$taskId"
        is AppScreen.Result -> "result:$taskId"
    }
}

private fun appScreenFromRoute(route: String): AppScreen {
    val separatorIndex = route.indexOf(':')
    val routeName = if (separatorIndex >= 0) route.substring(0, separatorIndex) else route
    val taskId = if (separatorIndex >= 0) route.substring(separatorIndex + 1) else ""
    val routeTaskId = taskId.takeIf(::isRouteSafeTaskId)
    return when (routeName) {
        "onboarding" -> AppScreen.Onboarding
        "home" -> AppScreen.Home
        "progress" -> AppScreen.Progress
        "settings" -> AppScreen.Settings
        "details" -> routeTaskId?.let(AppScreen::Details) ?: AppScreen.Home
        "timer" -> routeTaskId?.let(AppScreen::Timer) ?: AppScreen.Home
        "result" -> routeTaskId?.let(AppScreen::Result) ?: AppScreen.Home
        else -> AppScreen.Home
    }
}
