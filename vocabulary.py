import json
import os
import random

VOCAB_FILE = "vocabulary.json"

def load_vocab():
    if not os.path.exists(VOCAB_FILE):
        return {}
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        print("⚠️ Fichier JSON invalide ou corrompu. Réinitialisation du vocabulaire.")
        return {}

def save_vocab(vocab):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

def add_word(lesson, jp, fr):
    vocab = load_vocab()
    if lesson not in vocab:
        vocab[lesson] = []
    if any(entry["japanese"] == jp for entry in vocab[lesson]):
        print(f"❌ Le mot '{jp}' existe déjà dans la leçon {lesson}.")
        return
    # Permettre plusieurs traductions séparées par une virgule
    translations = [t.strip() for t in fr.split(",") if t.strip()]
    vocab[lesson].append({"japanese": jp, "french": translations})
    save_vocab(vocab)
    print(f"✅ Ajouté : {jp} - {', '.join(translations)} à la leçon {lesson}")

def remove_word(lesson, jp):
    vocab = load_vocab()
    if lesson not in vocab or not vocab[lesson]:
        print(f"⚠️ Aucun mot trouvé pour la leçon {lesson}.")
        return
    original_len = len(vocab[lesson])
    vocab[lesson] = [entry for entry in vocab[lesson] if entry["japanese"] != jp]
    if len(vocab[lesson]) == original_len:
        print(f"❌ Le mot '{jp}' n'existe pas dans la leçon {lesson}.")
        return
    save_vocab(vocab)
    print(f"🗑️ Supprimé : {jp} de la leçon {lesson}")

def romanize(japanese_word):
    # Chargement du mapping depuis le fichier JSON (une seule fois)
    if not hasattr(romanize, "kana_map"):
        with open("kana_map.json", "r", encoding="utf-8") as f:
            romanize.kana_map = json.load(f)
    kana_map = romanize.kana_map
    result = ''
    i = 0
    while i < len(japanese_word):
        # Gestion du petit tsu (っ ou ッ)
        if japanese_word[i] in ('っ', 'ッ'):
            # Chercher la prochaine syllabe (2 ou 1 caractères)
            next_romaji = ''
            if i+2 <= len(japanese_word) and japanese_word[i+1:i+3] in kana_map:
                next_romaji = kana_map[japanese_word[i+1:i+3]]
            elif i+1 < len(japanese_word) and japanese_word[i+1] in kana_map:
                next_romaji = kana_map[japanese_word[i+1]]
            if next_romaji:
                # Doubler la première consonne du prochain kana
                for c in next_romaji:
                    if c.isalpha():
                        result += c
                        break
            i += 1
            continue
        if i+1 < len(japanese_word) and japanese_word[i:i+2] in kana_map:
            result += kana_map[japanese_word[i:i+2]]
            i += 2
        elif japanese_word[i] in kana_map:
            result += kana_map[japanese_word[i]]
            i += 1
        else:
            result += japanese_word[i]
            i += 1
    return result

def start_quiz(lesson, n_questions, reverse=False):
    vocab = load_vocab()
    if lesson not in vocab or not vocab[lesson]:
        print(f"⚠️ Aucun mot trouvé pour la leçon {lesson}.")
        return
    words = vocab[lesson][:]
    random.shuffle(words)
    words = words[:n_questions]

    score = 0
    print(f"\n📖 Début du quiz ({'FR → JP' if reverse else 'JP → FR'}) : {len(words)} questions")
    print("Type '/t' à la place de la réponse pour afficher la traduction et transcription en cas de doute.")
    print("--------------------------------------------------")
    
    for entry in words:
        if reverse:
            question = ", ".join(entry["french"]) if isinstance(entry["french"], list) else entry["french"]
            expected = entry["japanese"]
            valid_answers = [expected.strip().lower()]
        else:
            question = entry["japanese"]
            valid_answers = [t.strip().lower() for t in entry["french"]] if isinstance(entry["french"], list) else [entry["french"].strip().lower()]
        answer = input(f"{question} : ")
        if not reverse and answer.strip() == "/t":
            print(f"Les bonnes réponses étaient : {', '.join(valid_answers)}")
            print(f"Romanisation : {romanize(question)}\n")
            # Pas d'incrément du score
        else:
            is_correct = any(answer.strip().lower() == valid for valid in valid_answers)
            if is_correct:
                print("✅ Correct !")
                score += 1
            else:
                print("❌ Faux.")
            # Toujours afficher la correction
            if reverse:
                print(f"La bonne réponse était : {expected}\n")
            else:
                print(f"Les bonnes réponses étaient : {', '.join(valid_answers)}\n")

    print(f"🎉 Score final : {score}/{len(words)}\n")

def list_lessons():
    vocab = load_vocab()
    if not vocab:
        print("⚠️ Aucune leçon trouvée.")
        return
    print("\n📚 Leçons disponibles :")
    for lesson, words in vocab.items():
        print(f" - {lesson} ({len(words)} mots et expressions)")
    print()

def list_words(lesson):
    vocab = load_vocab()
    if lesson not in vocab or not vocab[lesson]:
        print(f"⚠️ Aucun mot trouvé pour la leçon {lesson}.")
        return
    print(f"\n📖 Mots de la leçon {lesson} :")
    for entry in vocab[lesson]:
        # Afficher les traductions séparées par virgule
        fr = ", ".join(entry['french']) if isinstance(entry['french'], list) else entry['french']
        print(f" - {entry['japanese']} : {fr}")
    print()

def print_usage():
    print("""
📖 Commandes disponibles :

  add <leçon> <japonais> <français>
    ➝ Ajoute un mot à une leçon.

  remove <leçon> <japonais>
    ➝ Supprime un mot d'une leçon.

  start <leçon> <nombre> [reverse]
    ➝ Lance un quiz sur la leçon.
      [reverse] = optionnel, pour quiz FR → JP

  list
    ➝ Affiche les leçons disponibles.

  show <leçon>
    ➝ Affiche les mots d'une leçon.

  help
    ➝ Affiche cette aide.

  exit
    ➝ Quitte le programme.
""")

def main():
    print("📖 Bienvenue dans ton quiz de vocabulaire japonais 🇯🇵 !\nTape 'help' pour voir les commandes disponibles.\n")
    
    while True:
        cmd_input = input(">>> ").strip()
        if not cmd_input:
            continue

        parts = cmd_input.split()
        cmd = parts[0].lower()

        if cmd == "add" and len(parts) >= 4:
            lesson = parts[1]
            jp = parts[2]
            fr = " ".join(parts[3:])
            add_word(lesson, jp, fr)

        elif cmd == "remove" and len(parts) >= 3:
            lesson = parts[1]
            jp = parts[2]
            remove_word(lesson, jp)

        elif cmd == "start" and len(parts) >= 3:
            lesson = parts[1]
            try:
                n_questions = int(parts[2])
            except ValueError:
                print("⚠️ Le nombre de questions doit être un entier.")
                continue
            reverse = len(parts) > 3 and parts[3].lower() == "reverse"
            start_quiz(lesson, n_questions, reverse)

        elif cmd == "list":
            list_lessons()

        elif cmd == "show" and len(parts) == 2:
            lesson = parts[1]
            list_words(lesson)

        elif cmd == "help":
            print_usage()

        elif cmd in ("exit", "quit"):
            print("👋 À bientôt !")
            break

        else:
            print("⚠️ Commande inconnue. Tape 'help' pour voir les commandes disponibles.")

if __name__ == "__main__":
    main()