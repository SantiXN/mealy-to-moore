import csv
import sys


def read_mealy(mealy_filename):
    transitions = {}
    input_symbols = []

    with open(mealy_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)
        states = headers[1:]

        for row in reader:
            input_symbol = row[0]
            input_symbols.append(input_symbol)
            transitions[input_symbol] = {}

            for i, value in enumerate(row[1:], start=0):
                state = states[i]
                output, next_state = value.split('/')
                transitions[input_symbol][state] = (output, next_state)

    return transitions, states, input_symbols


def mealy_to_moore(mealy_filename, output_filename):
    transitions, states, input_symbols = read_mealy(mealy_filename)
    transitions, states = remove_unreachable_states_mealy(transitions, states, input_symbols)
    moore_transitions = {}
    old_to_new = extract_unique_sorted_tuples(transitions, states[0])

    for input_symbol in input_symbols:
        moore_transitions[input_symbol] = {}
        for old, new in old_to_new.items():
            state, output = old
            tuple = transitions[input_symbol][state]
            new_state = old_to_new[tuple]
            moore_transitions[input_symbol][new] = new_state

    outputs = {v: k[1] for k, v in old_to_new.items()}

    states = list(outputs.keys())
    print_moore(output_filename, moore_transitions, outputs, states, input_symbols)
    return moore_transitions, outputs, states, input_symbols


def moore_to_mealy(moore_filename, output_filename):
    transitions, outputs, states, input_symbols = read_moore(moore_filename)
    transitions, states = remove_unreachable_states_moore(transitions, states, input_symbols)
    mealy_transitions = {}

    for input_symbol in input_symbols:
        mealy_transitions[input_symbol] = {}
        for state in states:
            mealy_transitions[input_symbol][state] = (transitions[input_symbol][state], outputs[state])
    print_mealy("output1.csv", mealy_transitions, states, input_symbols)
    return mealy_transitions, states, input_symbols


def remove_unreachable_states_mealy(transitions, states, input_symbols):
    reachable_states = set()
    states_to_visit = {states[0]}

    while states_to_visit:
        current_state = states_to_visit.pop()
        reachable_states.add(current_state)

        for input_symbol in input_symbols:
            if current_state in transitions[input_symbol]:
                next_state, _ = transitions[input_symbol][current_state]
                if next_state not in reachable_states:
                    states_to_visit.add(next_state)

    for input_symbol in input_symbols:
        for state in list(transitions[input_symbol].keys()):
            if state not in reachable_states:
                del transitions[input_symbol][state]

    states = [state for state in states if state in reachable_states]

    return transitions, states


def remove_unreachable_states_moore(transitions, states, input_symbols):
    reachable_states = set()
    states_to_visit = {states[0]}

    while states_to_visit:
        current_state = states_to_visit.pop()
        reachable_states.add(current_state)

        for input_symbol in input_symbols:
            if current_state in transitions[input_symbol]:
                next_state = transitions[input_symbol][current_state]
                if next_state not in reachable_states:
                    states_to_visit.add(next_state)

    for input_symbol in input_symbols:
        for state in list(transitions[input_symbol].keys()):
            if state not in reachable_states:
                del transitions[input_symbol][state]

    states = [state for state in states if state in reachable_states]
    return transitions, states


def extract_unique_sorted_tuples(data, start):
    unique_tuples = set()
    for input_symbol, state_transitions in data.items():
        for state, (next_state, output) in state_transitions.items():
            unique_tuples.add((next_state, output))

    if not any(start == item[0] for item in unique_tuples):
        unique_tuples.add((start, ""))
    sorted_unique_tuples = sorted(unique_tuples)
    old_to_new = {}

    for idx, state_tuple in enumerate(sorted_unique_tuples):
        new_name = f'q{idx}'
        old_to_new[state_tuple] = new_name

    return old_to_new


def read_moore(moore_filename):
    transitions = {}
    states = []
    input_symbols = []
    outputs = {}

    with open(moore_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)
        output_symbols = headers[1:]
        states_row = next(reader)
        states = states_row[1:]

        for state, output_symbol in zip(states, output_symbols):
            outputs[state] = output_symbol

        for row in reader:
            input_symbol = row[0]
            input_symbols.append(input_symbol)
            transitions[input_symbol] = {}
            for i, state in enumerate(states):
                next_state = row[i + 1]
                transitions[input_symbol][state] = next_state

    return transitions, outputs, states, input_symbols


def print_mealy(output_filename, transitions, states, input_symbols):
    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        header = [''] + states
        writer.writerow(header)

        for input_symbol  in input_symbols:
            row = [input_symbol]
            for state in states:
                output, next_state = transitions[input_symbol].get(state, ('', ''))
                row.append(f'{output}/{next_state}')
            writer.writerow(row)


def print_moore(output_filename, transitions, outputs, states, input_symbols):
    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        header1 = [''] + list(outputs.values())
        writer.writerow(header1)
        header2 = [''] + states
        writer.writerow(header2)

        for input_symbol in input_symbols:
            row = [input_symbol]
            for state in states:
                next_state = transitions[input_symbol].get(state, '')
                row.append(next_state)
            writer.writerow(row)


def main():
    # if len(sys.argv) != 4:
    #     print("Использование:")
    #     print("Для преобразования из Mealy в Moore:")
    #     print("    program mealy-to-moore mealy.csv moore.csv")
    #     print("Для преобразования из Moore в Mealy:")
    #     print("    program moore-to-mealy moore.csv mealy.csv")
    #     sys.exit(1)

    command = "mealy-to-moore"
    input_file = "source_mealy.csv"
    output_file = "output.csv"

    if command == "mealy-to-moore":
        mealy_to_moore(input_file, output_file)
    elif command == "moore-to-mealy":
        moore_to_mealy(input_file, output_file)
    else:
        print(f"Неизвестная команда: {command}")
        print("Допустимые команды: 'mealy-to-moore' или 'moore-to-mealy'")
        sys.exit(1)


if __name__ == "__main__":
    main()