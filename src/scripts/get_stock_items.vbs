Call Main
 
Function CreateSQLAccServer
  Set CreateSQLAccServer = CreateObject("SQLAcc.BizApp")
End Function

Function Login(ByRef ComServer)
  Dim AccountId, Password, Dcf, Fdb
  AccountId = "ADMIN"
  Password = "ADMIN"
  Dcf = "C:\eStream\SQLAccounting\Share\Default.DCF"
  Fdb = "ACC-0001.FDB"

  If not ComServer.IsLogin Then 'if user hasn't logon to SQL application
    ComServer.Login AccountId, Password, Dcf, Fdb 
  END IF
End Function

Function Main
  Dim ComServer, lDateFrom, lDateTo

  Set ComServer = CreateSQLAccServer 'Create Com Server
  lDateFrom = CDate("January 01, 2000")
  lDateTo = CDate("December 31, 2050")

  Call Login(ComServer)

  Call GetStocks(ComServer, lDateFrom, lDateTo)
  Call GetCustomers(ComServer, lDateFrom, lDateTo)
End Function

Function GetStocks(ByRef ComServer, ByRef lDateFrom, ByRef lDateTo)
  Dim RptObject, lDataSet1

  Set RptObject = ComServer.RptObjects.Find("Stock.Item.RO") 
 
  RptObject.Params.Find("AllItem").AsBoolean              = true
  RptObject.Params.Find("AllStockGroup").AsBoolean        = true
  RptObject.Params.Find("AllCustomerPriceTag").AsBoolean  = true
  RptObject.Params.Find("AllSupplierPriceTag").AsBoolean  = true

  RptObject.Params.Find("HasAltStockItem").AsBoolean      = false
  RptObject.Params.Find("HasBarcode").AsBoolean           = false
  RptObject.Params.Find("HasBOM").AsBoolean               = false
  RptObject.Params.Find("HasCategory").AsBoolean          = false
  RptObject.Params.Find("HasCustomerItem").AsBoolean      = false
  RptObject.Params.Find("HasOpeningBalance").AsBoolean    = false
  RptObject.Params.Find("HasPurchasePrice").AsBoolean     = false
  RptObject.Params.Find("HasSellingPrice").AsBoolean      = false
  RptObject.Params.Find("HasSupplierItem").AsBoolean      = false
  RptObject.Params.Find("PrintActive").AsBoolean          = true
  RptObject.Params.Find("PrintInActive").AsBoolean        = true
  RptObject.Params.Find("PrintNonStockControl").AsBoolean = true
  RptObject.Params.Find("PrintStockControl").AsBoolean    = true
  RptObject.Params.Find("SelectCategory").AsBoolean       = false
  RptObject.Params.Find("SelectDate").AsBoolean           = false
  RptObject.Params.Find("SortBy").AsString                = "Code"
    
  RptObject.CalculateReport()
  Set lDataSet1 = RptObject.DataSets.Find("cdsMain")

  Dim Code, Description, Balance, Uom, RefPrice, RefCost
  lDataSet1.First
  While (not lDataSet1.eof)
    Code = lDataSet1.FindField("Code").AsString
    Description = lDataSet1.FindField("Description").AsString
    Balance = lDataSet1.FindField("BalSQty").AsString
    Uom = lDataSet1.FindField("UOM").AsString
    RefCost = lDataSet1.FindField("RefCost").AsString
    RefPrice = lDataSet1.FindField("RefPrice").AsString

    WScript.Echo "i=" & Code & "|" & Description & "|" & Balance & "|" & Uom & "|" & RefCost & "|" & RefPrice & "|"
    lDataSet1.Next
  Wend
End Function

Function GetCustomers(ByRef ComServer, ByRef lDateFrom, ByRef lDateTo)
  Dim RptObject, lDataSet, lDataSet2

  Set RptObject = ComServer.RptObjects.Find("Customer.RO") 

  RptObject.Params.Find("AllAgent").Value = true
  RptObject.Params.Find("AllArea").Value = true
  RptObject.Params.Find("AllCompany").Value = true
  RptObject.Params.Find("AllCompanyCategory").Value = true
  RptObject.Params.Find("AllCurrency").Value = true
  RptObject.Params.Find("AllTerms").Value = true
  RptObject.Params.Find("SelectDate").Value = true
  RptObject.Params.Find("PrintActive").Value = true
  RptObject.Params.Find("PrintInactive").Value = false
  RptObject.Params.Find("PrintPending").Value = false
  RptObject.Params.Find("PrintProspect").Value = false
  RptObject.Params.Find("PrintSuspend").Value = false

  RptObject.Params.Find("DateFrom").Value = lDateFrom
  RptObject.Params.Find("DateTo").Value = lDateTo

  
  RptObject.CalculateReport()
  Set lDataSet = RptObject.DataSets.Find("cdsMain")
  Set lDataSet2 = RptObject.DataSets.Find("cdsBranch")

  Dim CompanyCode, CompanyName
  Dim BranchName, Attention, Addr1, Addr2, Addr3, Addr4, Phone1, Phone2, Fax1, Fax2, Email
  lDataSet.First
  While (not lDataSet.eof)
    CompanyCode = lDataSet.FindField("Code").AsString
    CompanyName = lDataSet.FindField("CompanyName").AsString

    WScript.Echo "c=" & CompanyCode & "|" & CompanyName & "|"

    lDataSet2.First
    While (not lDataSet2.eof)
      BranchName = lDataSet2.FindField("BranchName").AsString
      Attention = lDataSet2.FindField("Attention").AsString
      Addr1 = lDataSet2.FindField("Address1").AsString
      Addr2 = lDataSet2.FindField("Address2").AsString
      Addr3 = lDataSet2.FindField("Address3").AsString
      Addr4 = lDataSet2.FindField("Address4").AsString
      Phone1 = lDataSet2.FindField("Phone1").AsString
      Phone2 = lDataSet2.FindField("Phone2").AsString
      Fax1 = lDataSet2.FindField("Fax1").AsString
      Fax2 = lDataSet2.FindField("Fax2").AsString
      Email = lDataSet2.FindField("Email").AsString

      WScript.Echo "b=" & CompanyCode & "|" & BranchName & "|" & Attention & "|" & Addr1 & "|" & Addr2 & "|" & Addr3 & "|" & Addr4 & "|" & Phone1 & "|" & Phone2 & "|" & Fax1 & "|" & Fax2 & "|" & Email & "|"

      lDataSet2.Next
    Wend
	lDataSet.Next
  Wend
End Function
