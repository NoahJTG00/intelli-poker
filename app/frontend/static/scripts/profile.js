document.addEventListener("DOMContentLoaded", function() {
    const achievements = {
        streak_progress: 80,
        streak_count: 24,
        champion_progress: 100,
        champion_count: 1,
        top_hand_progress: 50,
        top_hand_count: 1,
        overachiever_progress: 60,
        overachiever_count: 3
    };

    setTimeout(() => {
        document.querySelector(".achievement-item:nth-child(1) .progress").style.width = achievements.streak_progress + "%";
        document.querySelector(".achievement-item:nth-child(1) span").innerText = achievements.streak_count + "/30";

        document.querySelector(".achievement-item:nth-child(2) .progress").style.width = achievements.champion_progress + "%";
        document.querySelector(".achievement-item:nth-child(2) span").innerText = achievements.champion_count + "/1";

        document.querySelector(".achievement-item:nth-child(3) .progress").style.width = achievements.top_hand_progress + "%";
        document.querySelector(".achievement-item:nth-child(3) span").innerText = achievements.top_hand_count + "/2";

        document.querySelector(".achievement-item:nth-child(4) .progress").style.width = achievements.overachiever_progress + "%";
        document.querySelector(".achievement-item:nth-child(4) span").innerText = achievements.overachiever_count + "/5";
    }, 1000); // simulate a 1-second data fetch delay lol
});

function simulateGame() {
    const achievements = {
        streak_count: 24,
        streak_total: 30,
        champion_count: 1,
        champion_total: 1,
        top_hand_count: 1,
        top_hand_total: 2,
        overachiever_count: 3,
        overachiever_total: 5
    };

    achievements.streak_count++;
    achievements.overachiever_count++;

    const streak_progress = (achievements.streak_count / achievements.streak_total) * 100;
    const overachiever_progress = (achievements.overachiever_count / achievements.overachiever_total) * 100;

    document.querySelector(".achievement-item:nth-child(1) .progress").style.width = streak_progress + "%";
    document.querySelector(".achievement-item:nth-child(1) span").innerText = achievements.streak_count + "/" + achievements.streak_total;

    document.querySelector(".achievement-item:nth-child(4) .progress").style.width = overachiever_progress + "%";
    document.querySelector(".achievement-item:nth-child(4) span").innerText = achievements.overachiever_count + "/" + achievements.overachiever_total;
}