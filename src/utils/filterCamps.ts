// src/utils/filterCamps.ts
export const isValidCamp = (camp: any) => {
  return (
    camp.description && 
    camp.description.length > 20 && 
    camp.address
  );
};

export const getValidCampgrounds = (rawCamps: any[]) => {
  return rawCamps.filter(isValidCamp);
};