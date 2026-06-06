package ru.poryadok5.app.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

val Cream = Color(0xFFFBFAF7)
val Surface = Color(0xFFFFFFFF)
val Charcoal = Color(0xFF232824)
val MutedText = Color(0xFF617069)
val Sage = Color(0xFF496B5A)
val SageSoft = Color(0xFFDDE9D8)
val Blue = Color(0xFF4D6575)
val BlueSoft = Color(0xFFDDE8EE)
val Amber = Color(0xFFE6B84E)
val AmberSoft = Color(0xFFFFF0C2)
val Error = Color(0xFFB24D3E)

private val ColorScheme = lightColorScheme(
    primary = Sage,
    onPrimary = Color.White,
    primaryContainer = SageSoft,
    onPrimaryContainer = Charcoal,
    secondary = Blue,
    onSecondary = Color.White,
    secondaryContainer = BlueSoft,
    onSecondaryContainer = Charcoal,
    tertiary = Amber,
    onTertiary = Charcoal,
    tertiaryContainer = AmberSoft,
    onTertiaryContainer = Charcoal,
    background = Cream,
    onBackground = Charcoal,
    surface = Surface,
    onSurface = Charcoal,
    surfaceVariant = Color(0xFFE9E7E1),
    onSurfaceVariant = MutedText,
    error = Error,
)

private val AppTypography = Typography(
    displaySmall = Typography().displaySmall.copy(
        fontSize = 34.sp,
        lineHeight = 40.sp,
        fontWeight = FontWeight.Bold,
        color = Charcoal,
    ),
    headlineMedium = Typography().headlineMedium.copy(
        fontSize = 26.sp,
        lineHeight = 32.sp,
        fontWeight = FontWeight.Bold,
        color = Charcoal,
    ),
    titleLarge = Typography().titleLarge.copy(
        fontSize = 21.sp,
        lineHeight = 27.sp,
        fontWeight = FontWeight.SemiBold,
        color = Charcoal,
    ),
    titleMedium = Typography().titleMedium.copy(
        fontSize = 17.sp,
        lineHeight = 23.sp,
        fontWeight = FontWeight.SemiBold,
        color = Charcoal,
    ),
    bodyLarge = Typography().bodyLarge.copy(
        fontSize = 16.sp,
        lineHeight = 24.sp,
        color = Charcoal,
    ),
    bodyMedium = Typography().bodyMedium.copy(
        fontSize = 14.sp,
        lineHeight = 21.sp,
        color = MutedText,
    ),
    labelLarge = Typography().labelLarge.copy(
        fontSize = 15.sp,
        lineHeight = 20.sp,
        fontWeight = FontWeight.SemiBold,
    ),
)

private val AppShapes = Shapes(
    extraSmall = RoundedCornerShape(6.dp),
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(8.dp),
    large = RoundedCornerShape(8.dp),
    extraLarge = RoundedCornerShape(8.dp),
)

@Composable
fun PoryadokTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = ColorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content,
    )
}
