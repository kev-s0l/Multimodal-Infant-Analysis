def calculate_sleep_statistics(sleeps_stages):

    stage_counts = {}
    for stage in sleeps_stages:
        stage_counts[stage] = stage_counts.get(stage,0) + 1

    stage_minutes = {
        stage: count * 0.5
        for stage,count in stage_counts.items()
    }

    total_epochs = len(sleeps_stages)

    stage_percentage = {
        stage: (count / total_epochs) * 100
        for stage, count in stage_counts.items()
    }

    return stage_counts, stage_minutes, stage_percentage