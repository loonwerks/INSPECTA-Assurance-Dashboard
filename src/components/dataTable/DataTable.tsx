import { DataGrid, GridColDef, GridToolbar } from "@mui/x-data-grid";
import "./dataTable.scss";

type Props = {
    columns: GridColDef[],
    rows: Object[]
}

// const columns: GridColDef<(typeof rows)[number]>[] = [
//     { field: 'id', headerName: 'ID', width: 90 },
//     { field: 'runNum', headerName: 'Run Number', width: 150 },
//     {
//       field: 'itemName',
//       headerName: 'Name',
//       width: 150,
//     //   editable: true,
//     },
//     {
//       field: 'itemTitle',
//       headerName: 'Title',
//       width: 150,
//     //   editable: true,
//     },
//     {
//       field: 'itemConclusion',
//       headerName: 'Status',
//     //   type: 'number',
//       width: 110,
//     //   editable: true,
//     },
//     {
//       field: 'itemCreatedAt',
//       headerName: 'Created At',
//       description: 'This column has a value getter and is not sortable.',
//       sortable: false,
//       width: 160,
//     //   valueGetter: (value, row) => `${row.firstName || ''} ${row.lastName || ''}`,
//     },
//     {
//         field: 'itemActor',
//         headerName: 'Actor',
//         width: 150,
//       //   editable: true,
//       },
//       {
//         field: 'itemRepo',
//         headerName: 'Repository Name',
//         width: 150,
//       //   editable: true,
//       },
//   ];
  
//   const rows = [
//     { id: 1, lastName: 'Snow', firstName: 'Jon', age: 14 },
//     { id: 2, lastName: 'Lannister', firstName: 'Cersei', age: 31 },
//     { id: 3, lastName: 'Lannister', firstName: 'Jaime', age: 31 },
//     { id: 4, lastName: 'Stark', firstName: 'Arya', age: 11 },
//     { id: 5, lastName: 'Targaryen', firstName: 'Daenerys', age: null },
//     { id: 6, lastName: 'Melisandre', firstName: null, age: 150 },
//     { id: 7, lastName: 'Clifford', firstName: 'Ferrara', age: 44 },
//     { id: 8, lastName: 'Frances', firstName: 'Rossini', age: 36 },
//     { id: 9, lastName: 'Roxie', firstName: 'Harvey', age: 65 },
//   ];

const DataTable = (props: Props) => {
  return (
    <div className="dataTable">
        <DataGrid className="dataGrid"
            rows={props.rows}
            columns={props.columns}
            initialState={{
            pagination: {
                paginationModel: {
                pageSize: 5,
                },
            },
            }}
            slots={{toolbar: GridToolbar}}
            slotProps={{
                toolbar: {
                    showQuickFilter: true,
                    quickFilterProps: {debounceMs: 500}
                },
            }}
            pageSizeOptions={[5]}
            checkboxSelection
            disableRowSelectionOnClick
            disableColumnFilter
            disableColumnSelector
            disableDensitySelector
        />
    </div>
  )
}

export default DataTable