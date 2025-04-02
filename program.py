import pandas as pd

# Dictionary to store the flow mapping based on tSwitch status
switch_flow = {
    1: {1: 2, 2: 1, 3: 4, 4: 3},
    2: {1: 4, 4: 1, 2: 3, 3: 2},
    3: {1: 3, 3: 1, 2: 4, 4: 2}
}

def trace_flow(node_connect, node_define, current_node):
    """
    Iteratively trace the flow from the current node to find the destination.
    """
    current_port = 1  # Start from port 1 of the iNode
    path = [f"{current_node}({current_port})"]

    while True:
        # Search for the connection involving the current node and port
        connection = node_connect[
            ((node_connect['ID1'] == current_node) & (node_connect['ID1_port'] == current_port)) |
            ((node_connect['ID2'] == current_node) & (node_connect['ID2_port'] == current_port))
        ]

        if connection.empty:
            # No connection found, open circuit
            path.append("Open node")
            break

        # Get the connected object and port
        row = connection.iloc[0]
        if row['ID1'] == current_node:
            next_node = row['ID2']
            next_port = row['ID2_port']
        else:
            next_node = row['ID1']
            next_port = row['ID1_port']

        # Check if the next node is a tSwitch
        if node_define.loc[node_define['ID'] == next_node, 'Object'].values[0] == 'tSwitch':
            tSwitch_status = int(node_define.loc[node_define['ID'] == next_node, 'Status'].values[0])
            if tSwitch_status in switch_flow:
                # Update the port based on the tSwitch status
                output_port = switch_flow[tSwitch_status][next_port]
                path.append(f"{next_node}({next_port})({output_port})")
                current_node = next_node
                current_port = output_port
            else:
                # Invalid tSwitch status, treat as open circuit
                path.append("Open node")
                break
        else:
            # The flow has reached its destination (iNode or oNode)
            path.append(f"{next_node}({next_port})")
            break

    return path

def process_csv():
    try:
        # Read the CSV files into DataFrames
        node_define = pd.read_csv('node_define.csv')
        node_connect = pd.read_csv('node_connect.csv')

        # Prepare a list to store the flow results
        flow_results = []

        # Find all iNodes
        iNodes = node_define[node_define['Object'] == 'iNode']['ID'].tolist()

        # Trace the flow for each iNode
        for iNode in iNodes:
            path = trace_flow(node_connect, node_define, iNode)
            flow_results.append(" -> ".join(path))

        # Write the flow results to a text file
        with open('current_flow.txt', 'w') as f:
            for result in flow_results:
                f.write(result + '\n')

        print("Current flow has been exported to 'current_flow.txt'.")

    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    process_csv()