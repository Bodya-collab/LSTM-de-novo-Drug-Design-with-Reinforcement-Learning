# 6. QED vs AI Score
my_data <- read_csv("my_ai_molecules_full_QED.csv")
my_data <- na.omit(my_data)
ggplot(my_data, aes(x = QED, y = ai_score)) +
  geom_point(alpha = 0.4, color = "seagreen") +
  geom_smooth(method = "lm", color = "darkred", se = FALSE, linewidth = 1.2) +
  theme_minimal() +
  labs(title = "Quantitative Estimate of Druglikeness (QED) vs AI Score",
       x = "QED Score",
       y = "AI Score")